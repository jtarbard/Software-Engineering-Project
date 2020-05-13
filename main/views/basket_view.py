import flask
import datetime

import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
from main.data.db_classes.transaction_db_class import Membership
import main.view_lib.cookie_lib as cl
import main.view_lib.basket_lib as bl

blueprint = flask.Blueprint("basket", __name__)


@blueprint.route("/misc/add_booking_to_basket", methods=["POST"])
def add_booking_to_basket_post():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form
    activity = adf.return_activity_with_id(data_form.get('activity'))
    booking_amount: int = int(data_form.get("amount_of_people"))
    num_regular_sessions: int = int(data_form.get("num_regular_sessions"))

    if not activity or not booking_amount:
        flask.flash("Not checked out or booked activity", category="error")
        return flask.render_template("/misc/general_error.html", error="Not checked out or booked activity", has_cookie=has_cookie)

    is_valid, basket_activities, basket_membership, basket_membership_duration = \
        tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    # TODO: Discuss if this is the desired behaviour
    #       In Test_4,Test_5, it's expected to render general_error page
    if not is_valid:
        flask.flash("User is invalid. Please try to login again.", category="error")
        return cl.destroy_account_cookie(flask.redirect("/account/login"))

    if basket_activities:
        if (basket_membership and (len(basket_activities) + booking_amount > 14)) or len(
                basket_activities) + booking_amount > 15:
            flask.flash("Basket full", category="error")
            return flask.render_template("/misc/general_error.html", error="Basket full", User=user, has_cookie=has_cookie)

    spaces_left = activity.session_type.maximum_activity_capacity - len(
        tdf.return_bookings_with_activity_id(activity.activity_id))
    if spaces_left <= 0:
        flask.flash("Not enough spaces left on activity", category="error")
        return flask.render_template("/misc/general_error.html", error="Not enough spaces left on activity",
                                     User=user, has_cookie=has_cookie)

    # Add all selected regular sessions to the basket cookie
    response = cl.add_activity_or_membership_to_basket(
        booking_objects=adf.return_regular_activities_from(activity, limit=num_regular_sessions),
        request=flask.request,
        num_people=booking_amount
    )

    if not response:
        return flask.abort(500)

    session_type = adf.return_session_type_with_id(activity.session_type_id)
    flask.flash(session_type.session_type_name.title()+" session has been added to your basket.", category="success")

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@blueprint.route("/account/basket", methods=["GET"])
def basket_view():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    is_valid, basket_activities, basket_membership, basket_membership_duration \
        = tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid:
        flask.flash("User is invalid. Please try to login again.", category="error")
        return cl.destroy_account_cookie(flask.redirect("/account/login"))

    print(basket_membership, basket_activities)

    if not (basket_activities or basket_membership):
        return flask.render_template("/account/basket.html", User=user, has_cookie=has_cookie)

    new_activities_basket = ""
    redirect = False
    for activity in basket_activities:
        spaces_left = activity.session_type.maximum_activity_capacity - len(
            tdf.return_bookings_with_activity_id(activity.activity_id))
        number_of_activities = basket_activities.count(activity)
        if spaces_left >= number_of_activities and activity.start_time > datetime.datetime.now():
            if len(new_activities_basket) != 0:
                new_activities_basket += ";"
            new_activities_basket += "A:" + str(activity.activity_id)
        else:
            redirect = True

    if redirect:
        response = flask.redirect("/account/basket")
        response.set_cookie("vertex_basket_cookie", new_activities_basket, max_age=datetime.timedelta(days=1))
        return response

    regular_discounts = bl.return_regular_discounts(basket_activities)

    activity_and_price = dict()
    total_activity_price = 0
    for i, activity in enumerate(basket_activities):
        duration: datetime.timedelta = activity.end_time - activity.start_time
        current_price = (duration.seconds // 3600 * activity.session_type.hourly_activity_price)
        number_of_activities = basket_activities.count(activity)

        activity_and_price[activity] = (current_price, number_of_activities, regular_discounts[i])
        total_activity_price += current_price - (current_price * regular_discounts[i] / 100)  # TODO: Bad floating point for money

    current_membership_discount = 0
    memb_start_date = datetime.date.today()
    memb_end_date = None
    # total_discounted_price = 0  # can uncomment but this is not needed (why is python weird)
    if basket_membership:
        total_discounted_price = (total_activity_price - basket_membership.discount / 100 * total_activity_price)
        if memb_start_date.month+basket_membership_duration > 12:
            memb_end_date = datetime.date(memb_start_date.year+1, memb_start_date.month+basket_membership_duration-12, memb_start_date.day)
        elif memb_start_date.month+basket_membership_duration == 12:
            memb_end_date = datetime.date(memb_start_date.year + 1, memb_start_date.month, memb_start_date.day)
        else:
            memb_end_date = datetime.date(memb_start_date.year, memb_start_date.month+basket_membership_duration, memb_start_date.day)

        current_membership_discount = basket_membership.discount
        final_price = total_discounted_price + (basket_membership_duration * basket_membership.monthly_price)
    else:
        customer = udf.return_customer_with_user_id(user.user_id)
        if customer and customer.current_membership:
            customer_membership = Membership.query.filter_by(membership_id=customer.current_membership_id).first()

            total_discounted_price = total_activity_price - \
                                     customer_membership.membership_type.discount / 100 * total_activity_price
            current_membership_discount = customer_membership.membership_type.discount
            final_price = total_discounted_price
        else:
            total_discounted_price = total_activity_price
            final_price = total_activity_price

    return flask.render_template("/account/basket.html", basket_activities=basket_activities,
                                 basket_membership=basket_membership, User=user,
                                 total_activity_price=total_activity_price, has_cookie=has_cookie,
                                 activity_and_price=activity_and_price, final_price=round(final_price, 2),
                                 basket_membership_duration=basket_membership_duration,
                                 total_discounted_price=round(total_discounted_price, 2),
                                 current_membership_discount=current_membership_discount,
                                 membership_start_date=memb_start_date, membership_end_date=memb_end_date)


@blueprint.route("/account/basket", methods=["POST"])
def basket_delete_activity():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    data_form = flask.request.form

    import pprint
    pprint.pprint(data_form)

    if data_form.get("delete_basket"):
        return cl.destroy_basket_cookie(flask.redirect("/account/basket"))

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

    response = cl.change_items_with_id_from_cookie(item[1], num_change, flask.redirect("/account/basket"),
                                                   flask.request, is_activity=is_activity)

    if not response:
        flask.abort(500)
    return response
