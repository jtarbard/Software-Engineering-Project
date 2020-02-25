import flask
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import datetime
from main.data.db_classes.activity_db_class import Activity

blueprint = flask.Blueprint("activities", __name__)


@blueprint.route("/activities/timetable", methods=["GET"])
def view_classes():
    '''
    account_id = udf.check_valid_account_cookie(flask.request)  # Returns user ID from cookie
    user = None
    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)
    '''

    activity_list = adf.return_activities_between_dates(datetime.datetime.now(), datetime.datetime.now()+datetime.timedelta(days=14))
    return flask.render_template("/activities/classes.html", list=activity_list)


@blueprint.route("/activities/book", methods=["POST"])
def book_class():
    user_id = udf.check_valid_account_cookie(flask.request)
    if user_id is not None:
        # user is logged in

        activity_id = request.form['activity']
        activity = Activity.query.get(activity_id)
        if activity is None:
            # don't book anything
            print("Tried booking non-existing activity!")
            return flask.redirect("/activities")
        else:
            # now the user pays for the booking
            return flask.render_template("transactions/payments.html",activity=activity)
    else:
        # user is NOT logged in
        return flask.redirect("/account/login")


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
