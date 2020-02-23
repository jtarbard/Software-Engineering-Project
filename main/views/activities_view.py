import flask
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import datetime

blueprint = flask.Blueprint("activities", __name__)


@blueprint.route("/activities/view_classes", methods=["GET"])
def view_classes():
    account_id = udf.check_valid_account_cookie(flask.request)  # Returns user ID from cookie
    user = None
    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)

    activity_list = adf.return_activities_between_dates(datetime.datetime.now(), datetime.datetime.now()+datetime.timedelta(days=14))
    return flask.render_template("/activities/classes.html", User=user, list=activity_list)


@blueprint.route("/transaction/view_receipt", methods=["POST"])
def view_receipt():
    account_id = udf.check_valid_account_cookie(flask.request)  # Returns user ID from cookie
    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)
            return response
    else:
        return flask.redirect('/account/login')  # If the use does not have an account cookie then they are taken to the
        # login page

    data_form = flask.request.form
    activity = adf.return_activity_with_id(data_form.get('activity'))
    return flask.render_template("/activities/receipt.html", adctivity=activity, User=user) #ID=activity_id)