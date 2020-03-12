import os
from pyzbar.pyzbar import decode
from PIL import Image
import flask
import datetime
from werkzeug.utils import secure_filename
import cryptography

import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
import main.cookie_transaction as ct
from main.data.db_classes.transaction_db_class import Receipt

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
        return flask.render_template("/transactions/pay_card.html", total_price=total_price, User=user)

    pay = data_form.get('pay')
    if not pay:
        return flask.abort(404)

    # TODO: Add card detail handling here

    is_valid, basket_activities, basket_membership, basket_membership_duration = \
        tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid or not (basket_activities or basket_membership):
        response = flask.redirect("/")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    receipt_id = tdf.create_new_receipt(basket_activities, basket_membership, user, basket_membership_duration)

    if not receipt_id:
        flask.abort(500)

    encrypted_receipt = udf.hash_text(str(receipt_id) + "-" + str(user.user_id))

    response = flask.redirect(f"/transactions/receipts/{encrypted_receipt}")
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


@blueprint.route("/transactions/receipts/<path:encrypted_receipt>")
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
                                     encrypted_receipt=encrypted_receipt)


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
