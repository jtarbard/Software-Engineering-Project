import flask
import datetime
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
import main.data.transactions.employee_data_transaction as edf
from main.data.db_classes.transaction_db_class import Membership
from main.data.db_classes.user_db_class import Customer

blueprint = flask.Blueprint("activities", __name__)


@blueprint.route("/activities/view_classes", methods=["GET"])
def view_classes_get():
    # TODO: Comment (User name needs to exist)
    account_id = udf.check_valid_account_cookie(flask.request)  # Returns user ID from cookie
    user = None
    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)

    activity_dict = {}
    activity_list = adf.return_activities_between_dates(datetime.datetime.now(), datetime.datetime.now()+datetime.timedelta(days=14))

    for i, activity in enumerate(activity_list):
        activity_capacity = adf.return_activity_capacity_with_activity_type_id(activity.activity_type_id)
        activity_dict[activity_list[i]] = (activity_capacity-len(tdf.return_bookings_with_activity_id(activity.activity_id)))

    return flask.render_template("/activities/classes.html", User=user, activity_dict=activity_dict)


@blueprint.route("/activities/view_class/<int:activity_id>", methods=["GET"])
def view_class(activity_id: int):
    account_id = udf.check_valid_account_cookie(flask.request)  # Returns user ID from cookie
    user = None
    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)
            return response

    else:
        return flask.redirect('/account/login')

    activity = adf.return_activity_with_id(activity_id)
    if not activity:
        return flask.abort(404)

    spaces_left = activity.activity_type.maximum_activity_capacity-len(tdf.return_bookings_with_activity_id(activity.activity_id))
    if spaces_left <= 0:
        return flask.abort(404)

    allow_booking = True
    if type(user) is not Customer:
        allow_booking = False
        membership = None
    else:
        membership : Membership = udf.return_membership_for_customer_id(account_id)

    duration: datetime.timedelta = activity.end_time - activity.start_time
    session_price = (duration.seconds // 3600 * activity.activity_type.hourly_activity_price)

    final_price = session_price * (membership.membership_type.discount/100)

    return flask.render_template("/activities/class.html", activity=activity, session_price=round(session_price, 2),
                                 spaces_left=spaces_left, allow_booking=allow_booking, membership=membership,
                                 final_price=round(final_price, 2))


# TODO: Refactor heavily
@blueprint.route("/misc/add_booking_to_basket", methods=["POST"])
def view_classes_post():
    account_id = udf.check_valid_account_cookie(flask.request)  # Returns user ID from cookie
    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)
            return response

    else:
        return flask.redirect('/account/login')

    data_form = flask.request.form
    activity = adf.return_activity_with_id(data_form.get('activity'))
    booking_amount: int = int(data_form.get("amount_of_people"))

    check_out = data_form.get("checkout")
    check_out = True

    if not check_out and not activity:
        return flask.render_template("/misc/general_error.html", error="Not checked out or booked activity")

    is_valid, basket_activities, basket_membership = tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid:
        response = flask.redirect("/")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    if basket_activities:
        if (basket_membership and (len(basket_activities) + booking_amount > 14)) or len(basket_activities) + booking_amount > 15:
            return flask.render_template("/misc/general_error.html", error="Basket full")

    spaces_left = activity.activity_type.maximum_activity_capacity - len(tdf.return_bookings_with_activity_id(activity.activity_id))
    if spaces_left <= 0:
        return flask.render_template("/misc/general_error.html", error="Not enough spaces left on activity")

    if check_out:
        response = flask.redirect("/transactions/payment")
    else:
        response = flask.redirect("/activities/view_classes")

    valid = True
    if activity:
        add_instance = "A:" + str(activity.activity_id)

        if "vertex_basket_cookie" not in flask.request.cookies:
            response.set_cookie("vertex_basket_cookie", add_instance, max_age=datetime.timedelta(days=1))
            return response

        basket = flask.request.cookies["vertex_basket_cookie"]

        for i in range(booking_amount):
            basket += ";" + add_instance

        response.set_cookie("vertex_basket_cookie", basket , max_age=datetime.timedelta(days=1))
        return response

    if not valid:
        return flask.abort(500)

    return response


@blueprint.route("/transactions/payment", methods=["GET"])
def payment_get():
    account_id = udf.check_valid_account_cookie(flask.request)  # Returns user ID from cookie
    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)
            return response

    else:
        return flask.redirect('/account/login')

    is_valid, basket_activities, basket_membership = tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid or (len(basket_activities) == 0 and len(basket_membership) == 0):
        response = flask.redirect("/")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    for activity in basket_activities:
        spaces_left = activity.activity_type.maximum_activity_capacity - len(tdf.return_bookings_with_activity_id(activity.activity_id))
        if spaces_left <= 0:
            return flask.render_template("/misc/general_error.html", error="Not enough spaces left on activity")

    facility_names = []
    total_price = 0
    individual_prices = []
    for activity in basket_activities:
        duration: datetime.timedelta = activity.end_time - activity.start_time
        activity_type = adf.return_activity_type_with_id(activity.activity_type_id)
        current_price = (duration.seconds // 3600 * activity_type.hourly_activity_price)
        individual_prices.append(current_price)
        total_price += current_price

        facility_name = edf.return_facility_name_with_facility_id(activity.facility_id)
        if facility_name:
            facility_names.append(facility_name.capitalize())

    return flask.render_template("/transactions/payment", basket_activities=basket_activities,
                                 basket_membership=basket_membership, user=user, total_price=total_price,
                                 individual_prices=individual_prices)



