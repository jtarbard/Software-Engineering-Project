import flask
import datetime
#import cryptography
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
import main.cookie_transaction as ct
from main.data.db_classes.transaction_db_class import Receipt

blueprint = flask.Blueprint("transaction", __name__)


@blueprint.route("/transactions/pay-card", methods=["GET", "POST"])
def card_payment_post():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    #TODO: Add card detail handling here

    is_valid, basket_activities, basket_membership = tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if basket_activities:
        data_form = flask.request.form
        checkout = data_form.get('checkout')

        if checkout:
            total_price = data_form.get('total_price')
            return flask.render_template("/transactions/pay_card.html", total_price=total_price)

        pay = data_form.get('pay')
        if not pay:
            return flask.abort(404)

    if basket_membership and flask.request.method == "GET":
        total_price = basket_membership.monthly_price
        return flask.render_template("/transactions/pay_card.html", total_price=total_price)

    if not is_valid or not(basket_activities or basket_membership):
        response = flask.redirect("/")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    receipt_id = tdf.create_new_receipt(basket_activities, basket_membership, user)

    if not receipt_id:
        print("receipt id null")
        flask.abort(500)

    #TODO: Check if works
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
        return flask.render_template("/transactions/receipt.html", returned_receipt=returned_receipt)
