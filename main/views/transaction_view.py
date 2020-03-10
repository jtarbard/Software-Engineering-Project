import flask
import datetime
#import cryptography
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
import main.cookie_transaction as ct
from main.data.db_classes.transaction_db_class import Receipt
from main.data.db_classes.user_db_class import Customer, PaymentDetails
from main.data.db_session import add_to_database, delete_from_database

blueprint = flask.Blueprint("transaction", __name__)


@blueprint.route("/transactions/pay-card", methods=["POST"])
def card_payment_post():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    checkout = data_form.get('checkout')

    if checkout:
        total_price = data_form.get('total_price')

        payment_dictionary = {}

        if type(user) is Customer:
            customer = udf.return_customer_with_user_id(user.user_id)

            if customer.payment_detail is not None:
                payment_dictionary["card_number"] = customer.payment_detail.card_number
                payment_dictionary["start_date"] = customer.payment_detail.start_date
                payment_dictionary["expiration_date"] = customer.payment_detail.expiration_date
                payment_dictionary["street_and_number"] = customer.payment_detail.street_and_number
                payment_dictionary["town"] = customer.payment_detail.town
                payment_dictionary["city"] = customer.payment_detail.city
                payment_dictionary["postcode"] = customer.payment_detail.postcode

        return flask.render_template("/transactions/pay_card.html",
                                     total_price=total_price, User=user,
                                     payment_dictionary=payment_dictionary)

    pay = data_form.get('pay')
    if not pay:
        return flask.abort(404)

    #TODO: Add card detail handling here
    if type(user) is Customer:
        customer = udf.return_customer_with_user_id(user.user_id)

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

    is_valid, basket_activities, basket_membership = tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid or not(basket_activities or basket_membership):
        response = flask.redirect("/")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    receipt_id = tdf.create_new_receipt(basket_activities, basket_membership, user)

    if not receipt_id:
        flask.abort(500)

    encrypted_receipt = udf.hash_text(str(receipt_id) + "-" + str(user.user_id))

    response = flask.redirect(f"/transactions/receipts/{encrypted_receipt}")
    response.set_cookie("vertex_basket_cookie", "", max_age=0)
    return response


@blueprint.route("/transactions/receipts/<path:encrypted_receipt>")
def receipt_get(encrypted_receipt: str):
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response
    returned_receipt: Receipt = tdf.check_encrypted_receipt(encrypted_receipt, user)
    if not returned_receipt:
        return flask.abort(404)
    else:
        return flask.render_template("/transactions/receipt.html", returned_receipt=returned_receipt, User=user)


@blueprint.route("/transactions/refund", methods=["POST"])
def refund_booking():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    refund = data_form.get('refund')
    receipt = tdf.return_receipt_with_id(data_form.get("receipt_id"))
    activity = adf.return_activity_with_id(data_form.get('activity_id'))
    print(receipt)
    print(refund)
    print(activity)
    if not (refund and activity and receipt):
        return flask.abort(500)

    if not tdf.set_deletion_for_receipt_bookings_with_activity(receipt, activity):
        return flask.abort(500)

    return flask.redirect("/account/your_account")


