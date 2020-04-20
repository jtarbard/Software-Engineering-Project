import flask
import datetime
import json

import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
from main.data.db_classes.activity_db_class import Activity
from main.data.db_classes.transaction_db_class import Membership
from main.data.db_classes.user_db_class import Customer, Manager
import main.view_lib.cookie_lib as cl

blueprint = flask.Blueprint("activities", __name__)


@blueprint.route("/activities/types", methods=["POST", "GET"])
def view_activity_types():
    user, response, has_cookie = cl.return_user_response(flask.request, False)

    print(user, response, has_cookie)

    if response:
        return response

    # View a chosen activity type's booking
    if flask.request.method == "POST":
        data_form = flask.request.form
        request_activity_type_id = data_form.get("request_activity_type_id")

        return flask.redirect(flask.url_for("activities.view_booking", _method='GET', request_activity_type_id=request_activity_type_id))

    # = GET. View activity_types page (url is /activities/types)
    else:
        facilities = adf.return_facilities("Any")
        activity_types = adf.return_all_activity_types()

        return flask.render_template("/activities/activity_types.html", User=user, has_cookie=has_cookie,
                                     activity_types=activity_types, facilities=facilities, page_title="Activities")


@blueprint.route('/activities/booking', methods=["POST", "GET"])
def view_booking():
    user, response, has_cookie = cl.return_user_response(flask.request, False)
    if response:
        return response

    # Get data from request
    # data_form = flask.request.form
    # bulk_activities = data_form.getlist("bulk_activity")
    # start_time = data_form.get("start_time")
    # start_date = data_form.get("start_date")
    request_activity_type_id = flask.request.args.get("request_activity_type_id")
    print("args", flask.request.args)
    # facility_id = data_form.get("facility")

    is_valid, basket_activities, basket_membership, basket_membership_duration = \
        tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    # TODO: Hasn't this check already been done misc/add_to_booking???
    # if bulk_activities:
    #
    #     if not is_valid:
    #         return cl.destroy_account_cookie(flask.redirect("/"))
    #
    #     if basket_activities:
    #         if (basket_membership and len(basket_activities) > 14) or len(basket_activities) > 15:
    #             return flask.render_template("/misc/general_error.html", error="Basket full", User=user, has_cookie=has_cookie)
    #
    #     try:
    #         activity_type = adf.return_activity_with_id(bulk_activities[0]).activity_type
    #     except:
    #         return flask.abort(500)
    #
    #     added_activities = []
    #     for activity_id in bulk_activities:
    #         added_activity: Activity = adf.return_activity_with_id(activity_id)
    #         if not added_activity:
    #             return flask.abort(500)
    #
    #         if activity_type != added_activity.activity_type:
    #             return flask.abort(500)
    #
    #         if added_activity in added_activities:
    #             return flask.abort(500)
    #
    #         added_activities.append(added_activity)
    #         spaces_left = activity_type.maximum_activity_capacity - len(
    #             tdf.return_bookings_with_activity_id(activity_id))
    #
    #         if spaces_left <= 0:
    #             return flask.render_template("/misc/general_error.html", error="Not enough spaces left on activity",
    #                                          User=user, has_cookie=has_cookie)
    #
    #     response = cl.add_activities(added_activities, flask.request)
    #
    #     if not response:
    #         return flask.abort(500)
    #
    #     bulk_activity_type = adf.return_activity_type_name_with_activity_type_id(sent_activity)
    #     flask.flash(bulk_activity_type.title() + " sessions have been added to your basket.", category="success")
    #     return response

    # Filter check
    # if type(start_date) is str:
    #     start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    # if type(start_time) is str:
    #     try:
    #         start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
    #     except:
    #         start_time = datetime.datetime.strptime(start_time, "%H:%M:%S").time()

    # if not start_time:
    #     start_time = datetime.datetime.now().time()
    # if not start_date:
    #     start_date = datetime.date.today()
    # if not activity_type_id:
    #     activity_type_id = "Any"
    # elif activity_type_id != "Any":
    #     activity_type_id = int(activity_type_id)
    # if not facility_id:
    #     facility_id = "Any"
    # elif facility_id != "Any":
    #     facility_id = int(facility_id)

    # start_search = datetime.datetime.combine(start_date, start_time)

    # if start_search < datetime.datetime.now():
    #     start_search = datetime.datetime.now()

    activity_types = adf.return_activity_types("Any")

    facilities = adf.return_facilities("Any")

    if not facilities or not activity_types:
        flask.abort(500)

    session_availabilities = dict()

    weekly_activities = adf.return_weekly_activities_of_type(
        day=datetime.datetime.today(),
        activity_type_id=request_activity_type_id
    )

    activity_capacities = adf.return_activity_type_capacities()
    for session in weekly_activities:
        if basket_activities:
            amount_in_basket = basket_activities.count(session)
            if amount_in_basket >= 8:
                continue
        else:
            amount_in_basket = 0

        availability = activity_capacities[session.activity_type_id] - len(tdf.return_bookings_with_activity_id(session.activity_id)) - amount_in_basket
        if availability <= 0:
            continue

        session_availabilities[session] = availability

    # search_field_data = dict(start_date=start_date.strftime("%Y-%m-%d"),
    #                          min_date=datetime.date.today(),
    #                          max_date=datetime.date.today() + datetime.timedelta(days=14),  # ????????????
    #                          facility=facility_id,
    #                          activity=activity_type_id)
    # if start_date == datetime.date.today():
    #     search_field_data["min_time"] = datetime.datetime.now().strftime("%H:00:00")
    # else:
    #     search_field_data["min_time"] = datetime.datetime.now().strftime("00:00:00")
    # search_field_data["from_time"] = start_time.strftime("%H:00:00")

    return flask.render_template("/activities/booking.html",
                                 User=user,
                                 session_availabilities=session_availabilities,
                                 activity_types=activity_types,
                                 facilities=facilities,
                                 has_cookie=has_cookie,
                                 # search_field_data=search_field_data,
                                 request_activity_type_id=request_activity_type_id,
                                 page_title="Booking")


# -------------------------------------------------- Ajax routes -------------------------------------------------- #
@blueprint.route("/activities/query_sessions", methods=["POST"])
def query_sessions():
    """
    TODO: comment
    This route should only be accessible via the booking.html Ajax (method).

    :return: the sessions within the supplied date range
    """

    activity_type = flask.request.json.get("activity_type")
    activity_type_id = flask.request.json.get("activity_type_id")
    start_date = flask.request.json.get("start_date")
    end_date = flask.request.json.get("end_date")  # note: exclusive

    sessions = adf.return_activities_between_dates_of_type(start_date, end_date,
                                                           activity_type=activity_type,
                                                           activity_type_id=activity_type_id)
    data = list()
    for session in sessions:
        data.append(dict(id=session.activity_id,
                         name=session.activity_type.name.title(),
                         description=session.activity_type.description,
                         facility=session.facility.name,
                         start=session.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                         end=session.end_time.strftime("%Y-%m-%dT%H:%M:%S")))
    response = flask.make_response(json.dumps(data))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@blueprint.route("/activities/query_session", methods=["POST"])
def query_session():
    """

    This route should only be accessible via the booking.html Ajax (method).
    (This was previously view_activity())

    :return: the stringified session with the supplied id
    """

    status_code = 200

    id = flask.request.json.get("id")
    session = adf.return_activity_with_id(id)

    user, response, has_cookie = cl.return_user_response(flask.request, True)

    # ----- Error Checking ----- #
    if user is None:
        flask.flash("You need to login to view session details.", "error")  # TODO: Does this make sense?
        status_code = 300  # redirect

    # if response:
    #     flask.flash("You need to login to view session details.", "error")  # TODO: Does this make sense?
    #     return response

    if not session:
        flask.flash("This session does not exist.", "error")  # TODO: Severe error
        status_code = 404

    # ----- Retrieve data ----- #
    total_bookings = len(tdf.return_bookings_with_activity_id(session.activity_id))
    spaces_left = session.activity_type.maximum_activity_capacity - total_bookings
    duration: datetime.timedelta = session.end_time - session.start_time
    session_price = (duration.seconds // 3600 * session.activity_type.hourly_activity_price)  # TODO: Bad #135

    final_price = session_price

    session_dict = dict(
        user_role=user.__mapper_args__['polymorphic_identity'],
        minimum_age=session.activity_type.minimum_age,
        spaces_left=spaces_left,
        session_price=round(session_price, 2),  # TODO: Bad #135
        final_price=round(final_price, 2),  # TODO: Bad #135
        max_booking=min(spaces_left, 8)
    )

    # TODO: #135: Don't use floating point numbers for monetary calculation
    if type(user) is Manager:
        # TODO: Bad #135
        # TODO: Potential financial security flaw? The cost is openly accessible from the object, so what's stopping malicious users from getting those values?
        activity_income = total_bookings * session.activity_type.hourly_activity_price * (
                          session.end_time - session.start_time).seconds // 3600
        activity_cost = total_bookings * session.activity_type.hourly_activity_cost * (
                        session.end_time - session.start_time).seconds // 3600

        session_dict.update(dict(
            total_bookings=total_bookings,
            activity_cost=activity_cost,
            activity_income=activity_income
        ))
    elif type(user) is Customer and spaces_left > 0:
        customer = udf.return_customer_with_user_id(user.user_id)
        membership = customer.current_membership
        if membership is not None:
            membership_type = Membership.query.filter_by(membership_id=membership.membership_id).first().membership_type
            final_price = session_price * (1 - membership_type.discount / float(100))  # TODO: Bad #135

            session_dict.update(dict(
                final_price=round(final_price, 2),  # TODO: Bad #135
                membership_name=membership.name.title(),
                membership_discount=membership.discount
            ))

    # Don't check here. Check in js; also don't return sessions before today's date FOR CUSTOMER.
    # if a CUSTOMER clicks on an EXPIRED session, show that it's expired, and don't allow user to book the session
    # note that EMPLOYEE and MANAGER **CAN** still view the event details)
    # if activity.start_time < datetime.datetime.now() and type(user) is Customer:
    #     return flask.abort(404)

    response = flask.make_response(json.dumps(session_dict))
    response.status_code = status_code
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
