import os
from pyzbar.pyzbar import decode
from PIL import Image
import flask
import datetime
from werkzeug.utils import secure_filename
from flask import current_app as app
from flask_mail import Message, Mail
import qrcode


import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
import main.cookie_transaction as ct
from main.data.db_classes.transaction_db_class import Receipt
from main.data.db_classes.user_db_class import Customer, PaymentDetails, Employee
from main.data.db_session import add_to_database, delete_from_database

blueprint = flask.Blueprint("transaction", __name__)


@blueprint.route("/transactions/pay-card", methods=["POST"])
def card_payment_post():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    checkout = data_form.get('checkout')
    type = data_form.get("payment_type")
    customer_email = data_form.get("customer_email")

    if checkout:
        total_price = data_form.get('total_price')

        payment_dictionary = {}
        error = None

        if type == "card":
            if user.__mapper_args__ ['polymorphic_identity'] == "Customer":
                customer = udf.return_customer_with_user_id(user.user_id)
            else:
                customer = udf.return_customer_with_email(customer_email)
            if not customer_email:
                pass
            elif not customer:
                error = "Customer email could not be found"
            elif customer.payment_detail is not None:
                payment_dictionary["card_number"] = customer.payment_detail.card_number
                payment_dictionary["start_date"] = customer.payment_detail.start_date
                payment_dictionary["expiration_date"] = customer.payment_detail.expiration_date
                payment_dictionary["street_and_number"] = customer.payment_detail.street_and_number
                payment_dictionary["town"] = customer.payment_detail.town
                payment_dictionary["city"] = customer.payment_detail.city
                payment_dictionary["postcode"] = customer.payment_detail.postcode

            return flask.render_template("/transactions/pay_card.html",
                                     total_price=total_price, User=user, customer=customer,
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

            return flask.render_template("/transactions/pay_card.html",
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
        payment_detail = None
        if customer.payment_detail is not None:
            payment_detail = customer.payment_detail
        else:
            payment_detail = PaymentDetails()
            customer.payment_detail = payment_detail

        payment_detail.card_number = data_form.get('card_number')
        payment_detail.start_date = data_form.get('start_date')
        payment_detail.expiration_date = data_form.get('expiration_date')
        payment_detail.street_and_number = data_form.get('street_and_number')
        payment_detail.town = data_form.get('town')
        payment_detail.city = data_form.get('city')
        payment_detail.postcode = data_form.get('postcode')
        add_to_database(payment_detail)

    elif customer.payment_detail is not None:
        delete_from_database(customer.payment_detail)

    is_valid, basket_activities, basket_membership, basket_membership_duration = \
        tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid or not (basket_activities or basket_membership):
        response = flask.redirect("/")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    new_user = user
    if user.__mapper_args__['polymorphic_identity'] != "Customer":
        new_user = udf.return_user(customer.user_id)
        receipt_id = tdf.create_new_receipt(basket_activities, basket_membership, new_user, basket_membership_duration)
    else:
        receipt_id = tdf.create_new_receipt(basket_activities, basket_membership, user, basket_membership_duration)

    if not receipt_id:
        flask.abort(500)

    receipt = tdf.return_receipt_with_id(receipt_id)

    if not receipt:
        return flask.abort(500)

    if user.__mapper_args__['polymorphic_identity'] == "Employee":
        employee = udf.return_employee_with_user_id(user.user_id)
        employee.receipt_assist.append(receipt)
        add_to_database(employee)

    encrypted_receipt = udf.hash_text(str(receipt_id) + "-" + str(user.user_id))

    if user.__mapper_args__['polymorphic_identity'] != "Customer":
        response = flask.redirect(f"/transactions/view_individual_receipts/{receipt_id}")
    else:
        encrypted_receipt = udf.hash_text(str(receipt_id) + "-" + str(user.user_id))
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

        message = Message(f"Vertex Booking Receipt", recipients=[f"{new_user.email}"])
        message.html = """"<h1>Thank you for purchasing at The Vertex</h1> <br>
                           <h3>Receipt:</h3>
                           <table> 
                                <thead>
                                    <tr><td colspan="4"><h6> Classes brought &nbsp</h6></td></tr>
                                </head>
                                <tbody> 
                                    <tr> 
                                        <td><strong>Class Name &nbsp</strong></td>
                                        <td><strong>Class Start Time &nbsp</strong></td>
                                        <td><strong>Class End Time &nbsp</strong></td>
                                        <td><strong>Facility &nbsp</strong></td>
                                    </tr>
                                    <tr>
                                    """
        for booking in receipt.bookings:
            message.html += f"""
                <tr>
                    <td>{ booking.activity.activity_type.name }</td>
                    <td>{ booking.activity.start_time }</td>
                    <td>{ booking.activity.end_time }</td>
                    <td>{ booking.activity.facility.name }</td>
                <tr>
                """

        if receipt.membership:
            message.html += f"""
                <tr>
                    <td colspan="4" rowspan="1"></td>
                </tr>
                <tr>
                    <td colspan="4"><h6>Membership</h6></td>
                </tr>
                <tr> 
                    <td><strong>Membership Name &nbsp</strong></td>
                    <td><strong>Start Time &nbsp</strong></td>
                    <td><strong>End Time &nbsp</strong></td>
                    <td><strong>Discount &nbsp</strong></td>
                </tr>
                <tr> 
                    <td>{receipt.membership.membership_type.name} &nbsp</td>
                    <td>{receipt.membership.start_date} &nbsp</td>
                    <td>{receipt.membership.start_date} &nbsp</td>
                    <td>{receipt.membership.membership_type.discount} &nbsp</td>
                </tr>
            """
        message.html += f"""
                <tr>
                    <td colspan="2"></td>
                    <td><strong>Total Price: &nbsp</strong></td>
                    <td>{receipt.total_cost}</td>
                </tr>
            </tbody>
        </table>
        """

        file_direct = os.path.join("tmp", str(user.user_id) + datetime.datetime.now().strftime("-%m-%d-%Y-%H-%M-%S") + ".png")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(encrypted_receipt)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_direct)

        with app.open_resource("../"+file_direct) as fp:
            message.attach("Vertex_Receipt_"+str(receipt_id), "image/png", fp.read())

        try:
            mail.send(message)
        except:
            pass

        os.remove(file_direct)

    response.set_cookie("vertex_basket_cookie", "", max_age=0)
    return response


@blueprint.route("/transactions/receipts/check_receipt_input", methods=["POST"])
def check_receipt_qr_code():
    user, response = ct.return_user_response(flask.request, True)
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
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    try:
        returned_receipt: Receipt = tdf.check_encrypted_receipt(encrypted_receipt, user)
    except:
        return flask.abort(404)
    else:
        return flask.render_template("/transactions/receipt.html", returned_receipt=returned_receipt,
                                     encrypted_receipt=encrypted_receipt, User=user)


@blueprint.route("/transactions/view_individual_receipts/<int:receipt_id>", methods=["GET"])
def e_m_get(receipt_id: int):
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    returned_receipt: Receipt = tdf.return_receipt_with_id(receipt_id)

    if not returned_receipt:
        return flask.abort(404)

    customer_of_receipt = returned_receipt.customer_id

    encrypted_receipt = udf.hash_text(str(receipt_id) + "-" + str(customer_of_receipt))

    if user.__mapper_args__['polymorphic_identity'] == "Employee":
        employee: Employee = udf.return_employee_with_user_id(user.user_id)
        print(employee.receipt_assist)
        if returned_receipt in employee.receipt_assist:
            return flask.render_template("/transactions/receipt.html", returned_receipt=returned_receipt,
                                         User=customer_of_receipt, encrypted_receipt=encrypted_receipt)

    elif user.__mapper_args__['polymorphic_identity'] == "Manager":
        return flask.render_template("/transactions/receipt.html", returned_receipt=returned_receipt,
                                     User=customer_of_receipt, encrypted_receipt=encrypted_receipt)

    return flask.abort(404)


@blueprint.route("/transactions/refund", methods=["POST"])
def refund_booking():
    user, response = ct.return_user_response(flask.request, True)
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

    return flask.redirect("/account/your_account")
