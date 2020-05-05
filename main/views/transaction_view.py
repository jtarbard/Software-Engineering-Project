import os
from pyzbar.pyzbar import decode
from PIL import Image
import flask
import datetime
from flask import current_app as app
from flask_mail import Mail


import main.view_lib.transaction_lib as tl
import main.helper_functions.cryptography as crypt
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
import main.view_lib.cookie_lib as cl
import main.data.db_session as ds
from main.data.db_classes.transaction_db_class import Receipt
from main.data.db_classes.user_db_class import Employee

blueprint = flask.Blueprint("transaction", __name__)


@blueprint.route("/transactions/pay-card", methods=["POST"])
def card_payment_post():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    checkout = data_form.get('checkout')
    type = data_form.get("payment_type")
    customer_email = data_form.get("customer_email")

    is_valid, basket_activities, basket_membership, basket_membership_duration = \
        tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not (basket_activities or basket_membership) or not is_valid:
        return flask.redirect("/")

    if checkout:
        total_price = data_form.get('total_price')

        payment_dictionary = {}
        error = None

        if type == "card":
            if user.__mapper_args__ ['polymorphic_identity'] == "Customer":
                customer = udf.return_customer_with_user_id(user.user_id)
            else:
                customer = udf.return_customer_with_email(customer_email)

            if customer.payment_detail:
                payment_dictionary = vars(customer.payment_detail)

            return flask.render_template("/transactions/pay_card.html",
                                     total_price=total_price, User=user, customer=customer, has_cookie=has_cookie,
                                     payment_dictionary=payment_dictionary, error=error, type=type, checkout=True)

        elif type == "cash":
            if user.__mapper_args__['polymorphic_identity'] == "Customer":
                return flask.abort(500)
            else:
                if customer_email:
                    customer = udf.return_customer_with_email(customer_email)
                    if not customer:
                        error = "Customer email could not be found"
                else:
                    customer = None

            return flask.render_template("/transactions/pay_card.html", has_cookie=has_cookie,
                                         total_price=total_price, User=user, customer=customer,
                                         error=error, type=type, checkout=True)

    pay = data_form.get('pay')
    if not pay:
        return flask.abort(404)

    if user.__mapper_args__ ['polymorphic_identity'] == "Customer":
        customer = udf.return_customer_with_user_id(user.user_id)
    else:
        if not customer_email:
            return flask.abort(500)
        customer = udf.return_customer_with_email(customer_email)

    check_box = flask.request.form.get("remember_card_details")

    if check_box == "on":
        tdf.add_new_card_details(customer, card_number=data_form.get('card_number'), start_date=data_form.get('start_date'),
                                 expiration_date=data_form.get('expiration_date'),
                                 street_and_number=data_form.get('street_and_number'),
                                 town=data_form.get('town'), city=data_form.get('city'),
                                 postcode=data_form.get('postcode'))

    new_user = user
    if user.__mapper_args__['polymorphic_identity'] != "Customer":
        new_user = udf.return_user(customer.user_id)
        receipt_id = tdf.create_new_receipt(basket_activities, basket_membership,
                                            new_user, basket_membership_duration)
    else:
        receipt_id = tdf.create_new_receipt(basket_activities, basket_membership,
                                            user, basket_membership_duration)

    if not receipt_id:
        flask.abort(500)

    receipt = tdf.return_receipt_with_id(receipt_id)

    if not receipt:
        return flask.abort(500)

    if user.__mapper_args__['polymorphic_identity'] == "Employee":
        employee = udf.return_employee_with_user_id(user.user_id)
        employee.receipt_assist.append(receipt)
        ds.add_to_database(employee)

    encrypted_receipt = crypt.hash_text(str(receipt_id) + "-" + str(user.user_id))

    if user.__mapper_args__['polymorphic_identity'] != "Customer":
        response = flask.redirect(f"/transactions/view_individual_receipts/{receipt_id}")
    else:
        response = flask.redirect(f"/transactions/receipts/{encrypted_receipt}")

    with app.app_context():
        app.config["MAIL_USE_TLS"] = False
        app.config["MAIL_USE_SSL"] = True
        app.config["MAIL_PORT"] = 465
        app.config["MAIL_SERVER"] = "smtp.gmail.com"
        app.config["MAIL_USERNAME"] = "vertexleeds@gmail.com"
        app.config["MAIL_DEFAULT_SENDER"] = "vertexleeds@gmail.com"
        app.config["MAIL_PASSWORD"] = "WeAreTeam10"

        mail = Mail(app)

        message = tl.return_email_message(receipt, new_user)

        file_direct = os.path.join("tmp", str(user.user_id) + datetime.datetime.now().strftime("-%m-%d-%Y-%H-%M-%S") + ".png")

        tl.create_new_qrcode_image(file_direct, encrypted_receipt)

        with app.open_resource("../"+file_direct) as fp:
            message.attach("Vertex_Receipt_"+str(receipt_id), "image/png", fp.read())

        try:
            mail.send(message)
        except:
            pass

        os.remove(file_direct)

    response = cl.destroy_basket_cookie(response)

    return response


@blueprint.route("/transactions/receipts/check_receipt_input", methods=["POST"])
def check_receipt_qr_code():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    if 'file' not in flask.request.files:
        return flask.redirect("/account/your_account")

    receipt_file = flask.request.files["file"]

    if len(receipt_file.filename) < 1:
        return flask.redirect("/account/your_account")

    if receipt_file and receipt_file.filename.rsplit(".", 1)[1].lower() in ["png", "jpg", "jpeg"]:

        file_direct = os.path.join("tmp", str(user.user_id) + datetime.datetime.now().strftime("-%m-%d-%Y-%H-%M-%S") \
                                   + "." + receipt_file.filename.rsplit(".", 1)[1].lower())
        receipt_file.save(file_direct)

        try:
            data = decode(Image.open(file_direct))
            encrypted_receipt = data[0][0].decode("utf-8")
        except:
            return flask.redirect("/account/your_account")

        os.remove(file_direct)
        response = flask.redirect(f"/transactions/receipts/{encrypted_receipt}")
        return response

    else:
        return flask.redirect("/account/your_account")


@blueprint.route("/transactions/receipts/<path:encrypted_receipt>", methods=["GET"])
def receipt_get(encrypted_receipt: str):
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    try:
        returned_receipt: Receipt = tdf.check_encrypted_receipt(encrypted_receipt, user)
    except:
        return flask.abort(404)
    else:
        return flask.render_template("/transactions/receipt.html", returned_receipt=returned_receipt,
                                     encrypted_receipt=encrypted_receipt, User=user, has_cookie=has_cookie)


@blueprint.route("/transactions/view_individual_receipts/<int:receipt_id>", methods=["GET"])
def e_m_get(receipt_id: int):
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    returned_receipt: Receipt = tdf.return_receipt_with_id(receipt_id)

    if not returned_receipt:
        return flask.abort(404)

    customer_of_receipt = returned_receipt.customer_id

    encrypted_receipt = crypt.hash_text(str(receipt_id) + "-" + str(customer_of_receipt))

    if user.__mapper_args__['polymorphic_identity'] == "Employee":
        employee: Employee = udf.return_employee_with_user_id(user.user_id)
        print(employee.receipt_assist)
        if returned_receipt in employee.receipt_assist:
            return flask.render_template("/transactions/receipt.html", returned_receipt=returned_receipt,
                                         User=customer_of_receipt, encrypted_receipt=encrypted_receipt, has_cookie=has_cookie)

    elif user.__mapper_args__['polymorphic_identity'] == "Manager":
        return flask.render_template("/transactions/receipt.html", returned_receipt=returned_receipt,
                                     User=customer_of_receipt, encrypted_receipt=encrypted_receipt, has_cookie=has_cookie)

    return flask.abort(404)


@blueprint.route("/transactions/refund", methods=["POST"])
def refund_booking():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    refund = data_form.get('refund')
    receipt = tdf.return_receipt_with_id(data_form.get("receipt_id"))
    activity = adf.return_activity_with_id(data_form.get('activity_id'))
    if not (refund and activity and receipt):
        return flask.abort(500)

    if not tdf.set_deletion_for_receipt_bookings_with_activity(receipt, activity):
        return flask.abort(500)

    activity_type = adf.return_session_type_name_with_activity_type_id(activity.activity_type_id).title()
    flask.flash(activity_type+" booking refunded.", "success")

    return flask.redirect("/account/bookings")
