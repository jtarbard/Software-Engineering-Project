import flask
import datetime
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
import main.data.transactions.employee_data_transaction as edf
from main.data.db_classes.transaction_db_class import Membership
from main.data.db_classes.user_db_class import Customer
import main.cookie_transaction as ct

blueprint = flask.Blueprint("activities", __name__)


@blueprint.route("/activities/view_classes", methods=["GET"])
def view_classes_get():
    user, response = ct.return_user_response(flask.request, False)
    if response:
        return response

    activity_dict = {}
    activity_list = adf.return_activities_between_dates(datetime.datetime.now(), datetime.datetime.now()+datetime.timedelta(days=14))

    for i, activity in enumerate(activity_list):
        activity_capacity = adf.return_activity_capacity_with_activity_type_id(activity.activity_type_id)
        activity_dict[activity_list[i]] = (activity_capacity-len(tdf.return_bookings_with_activity_id(activity.activity_id)))

    return flask.render_template("/activities/classes.html", User=user, activity_dict=activity_dict)


@blueprint.route("/activities/view_class/<int:activity_id>", methods=["GET"])
def view_class(activity_id: int):
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    activity = adf.return_activity_with_id(activity_id)
    if not activity:
        return flask.abort(404)

    spaces_left = activity.activity_type.maximum_activity_capacity-len(tdf.return_bookings_with_activity_id(activity.activity_id))

    allow_booking = True
    if type(user) is not Customer or spaces_left <= 0:
        allow_booking = False
        membership = None
    else:
        customer = udf.return_customer_with_user_id(user.user_id)
        membership = customer.current_membership


    duration: datetime.timedelta = activity.end_time - activity.start_time
    session_price = (duration.seconds // 3600 * activity.activity_type.hourly_activity_price)

    final_price = session_price
    if membership:
        final_price = session_price * (membership.membership_type.discount/100)

    return flask.render_template("/activities/class.html", activity=activity, session_price=round(session_price, 2),
                                 spaces_left=spaces_left, allow_booking=allow_booking, membership=membership,
                                 final_price=round(final_price, 2), User=user)


# TODO: Refactor heavily
@blueprint.route("/misc/add_booking_to_basket", methods=["POST"])
def view_classes_post():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    activity = adf.return_activity_with_id(data_form.get('activity'))
    booking_amount: int = int(data_form.get("amount_of_people"))

    if not activity:
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

    response = flask.redirect("/activities/view_classes")

    valid = True
    if activity:
        add_instance = "A:" + str(activity.activity_id)

        if "vertex_basket_cookie" not in flask.request.cookies:
            basket = add_instance
            for i in range(booking_amount-1):
                basket += ";" + add_instance

            response.set_cookie("vertex_basket_cookie", basket, max_age=datetime.timedelta(days=1))
            return response

        basket = flask.request.cookies["vertex_basket_cookie"]

        for i in range(booking_amount):
            basket += ";" + add_instance

        response.set_cookie("vertex_basket_cookie", basket, max_age=datetime.timedelta(days=1))
        return response

    if not valid:
        return flask.abort(500)

    return response


@blueprint.route("/account/basket", methods=["GET"])
def basket_view():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    is_valid, basket_activities, basket_membership = tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid:
        response = flask.redirect("/")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    if not (basket_activities or basket_membership):
        return flask.render_template("/account/basket.html")

    new_activities_basket = ""
    redirect = False
    for activity in basket_activities:
        spaces_left = activity.activity_type.maximum_activity_capacity - len(tdf.return_bookings_with_activity_id(activity.activity_id))
        number_of_activities = basket_activities.count(activity)
        if spaces_left >= number_of_activities:
            if len(new_activities_basket) != 0:
                new_activities_basket += ";"
            new_activities_basket += "A:" + str(activity.activity_id)
        else:
            redirect = True

    if redirect:
        response = flask.redirect("/account/basket")
        response.set_cookie("vertex_basket_cookie", new_activities_basket, max_age=datetime.timedelta(days=1))
        return response

    activity_and_price = dict()
    total_price = 0
    for activity in basket_activities:
        duration: datetime.timedelta = activity.end_time - activity.start_time
        current_price = (duration.seconds // 3600 * activity.activity_type.hourly_activity_price)
        number_of_activities = basket_activities.count(activity)
        activity_and_price[activity] = (current_price, number_of_activities)
        total_price += current_price

    return flask.render_template("/account/basket.html", basket_activities=basket_activities,
                                 basket_membership=basket_membership, User=user, total_price=total_price,
                                 activity_and_price=activity_and_price)



