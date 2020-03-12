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

    if activity.start_time < datetime.datetime.now() and type(user) is Customer:
        return flask.abort(404)

    duration: datetime.timedelta = activity.end_time - activity.start_time
    session_price = (duration.seconds // 3600 * activity.activity_type.hourly_activity_price)

    final_price = session_price
    if membership:
        membership = Membership.query.filter_by(membership_id=membership).first().membership_type
        final_price = session_price * (1 - membership.discount/float(100))

    return flask.render_template("/activities/class.html", activity=activity, session_price=round(session_price, 2),
                                 spaces_left=spaces_left, allow_booking=allow_booking, membership=membership,
                                 final_price=round(final_price, 2), User=user, max_booking=min(spaces_left, 8))


@blueprint.route("/misc/add_booking_to_basket", methods=["POST"])
def view_classes_post():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    activity = adf.return_activity_with_id(data_form.get('activity'))
    booking_amount: int = int(data_form.get("amount_of_people"))
    mmembership = data_form.get('membership')

    if not activity or not booking_amount:
        return flask.render_template("/misc/general_error.html", error="Not checked out or booked activity")

    is_valid, basket_activities, basket_membership, basket_membership_duration = \
        tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid:
        response = flask.redirect("/")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    if basket_activities:
        if (basket_membership and (len(basket_activities) + booking_amount > 14)) or len(basket_activities) + booking_amount > 15:
            return flask.render_template("/misc/general_error.html", error="Basket full", User=user)

    spaces_left = activity.activity_type.maximum_activity_capacity - len(tdf.return_bookings_with_activity_id(activity.activity_id))
    if spaces_left <= 0:
        return flask.render_template("/misc/general_error.html", error="Not enough spaces left on activity", User=user)

    response = ct.add_activity_or_membership_to_basket(activity, flask.request, num_people=booking_amount)

    if not response:
        return flask.abort(500)

    return response


@blueprint.route("/account/basket", methods=["GET"])
def basket_view():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    is_valid, basket_activities, basket_membership, basket_membership_duration \
        = tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid:
        response = flask.redirect("/account/basket")
        response.set_cookie("vertex_basket_cookie", "", max_age=0)
        return response

    if not (basket_activities or basket_membership):
        return flask.render_template("/account/basket.html", User=user)

    new_activities_basket = ""
    redirect = False
    for activity in basket_activities:
        spaces_left = activity.activity_type.maximum_activity_capacity - len(tdf.return_bookings_with_activity_id(activity.activity_id))
        number_of_activities = basket_activities.count(activity)
        if spaces_left >= number_of_activities and activity.start_time > datetime.datetime.now():
            if len(new_activities_basket) != 0:
                new_activities_basket += ";"
            new_activities_basket += "A:" + str(activity.activity_id)
        else:
            print(activity.start_time > datetime.datetime.now())
            redirect = True

    if redirect:
        response = flask.redirect("/account/basket")
        response.set_cookie("vertex_basket_cookie", new_activities_basket, max_age=datetime.timedelta(days=1))
        return response

    activity_and_price = dict()
    total_activity_price = 0
    for activity in basket_activities:
        duration: datetime.timedelta = activity.end_time - activity.start_time
        current_price = (duration.seconds // 3600 * activity.activity_type.hourly_activity_price)
        number_of_activities = basket_activities.count(activity)
        activity_and_price[activity] = (current_price, number_of_activities)
        total_activity_price += current_price

    current_membership_discount = 0
    total_discounted_price = 0
    if basket_membership:
        total_discounted_price = (total_activity_price - basket_membership.discount/100 * total_activity_price)

        current_membership_discount =  basket_membership.discount
        final_price = total_discounted_price + (basket_membership_duration * basket_membership.monthly_price)
    else:
        customer = udf.return_customer_with_user_id(user.user_id)
        if customer.current_membership is not None:
            total_discounted_price = total_activity_price - \
                                     customer.current_membership.membership_type.discount/100 * total_activity_price
            current_membership_discount = customer.current_membership.membership_type.discount

        final_price = total_discounted_price

    return flask.render_template("/account/basket.html", basket_activities=basket_activities,
                                 basket_membership=basket_membership, User=user, total_activity_price=total_activity_price,
                                 activity_and_price=activity_and_price, final_price=round(final_price,2),
                                 basket_membership_duration=basket_membership_duration,
                                 total_discounted_price=round(total_discounted_price,2),
                                 current_membership_discount=current_membership_discount)


@blueprint.route("/account/basket", methods=["POST"])
def basket_delete_activity():
    user, response = ct.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    booking = data_form.get("update")
    booking_data = data_form.get("booking_id")
    num_change = int(data_form.get("num_change"))
    if not (booking and booking_data) or num_change > 8 or num_change < 0:
        return flask.abort(500)

    item = booking_data.split(":")
    if item[0] == "A":
        num_items = 2
        is_activity = True
    elif item[0] == "M":
        num_items = 3
        is_activity = False
    else:
        return flask.abort(500)

    if len(item) != num_items:
        return flask.abort(500)
    response = ct.change_items_with_id_from_cookie(item[1], num_change, flask.redirect("/account/basket"), flask.request, is_activity=is_activity)

    if not response:
        flask.abort(500)
    return response