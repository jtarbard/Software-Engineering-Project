import flask
import datetime
import json

import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
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

    if flask.request.method == "POST":
        request_activity_type_id = flask.request.form.get("request_activity_type_id")

        # View a chosen activity type's booking, or view all activities and filter as desired
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

    # Get this from the url argument (?request_activity_type_id=...)
    request_activity_type_id = flask.request.args.get("request_activity_type_id")
    filter_facility_type_id = flask.request.args.get("filter_facility_type_id")

    facilities = adf.return_facilities_with_facility_type_id(filter_facility_type_id)

    activity_type = adf.return_activity_type_with_id(request_activity_type_id)
    # The supplied id can be invalid, or the url doesn't contain a supplied id - in this case, it indicates the "show all" page is requested
    session_types = adf.return_session_types_with_activity_type_id(request_activity_type_id)

    page_title = "Booking" if activity_type is None else "Book " + activity_type.name.title()

    return flask.render_template("/activities/booking.html",
                                 User=user,
                                 has_cookie=has_cookie,
                                 activity_type=activity_type,  # For query_sessions
                                 facility_id_list=[facility.facility_id for facility in facilities],  # For predefined facility filtering
                                 session_types=session_types,
                                 facilities=adf.return_facilities("Any"),
                                 page_title=page_title)


# -------------------------------------------------- Ajax routes -------------------------------------------------- #
@blueprint.route("/activities/query_sessions", methods=["POST"])
def query_sessions():
    """
    TODO: comment
    This route should only be accessible via the booking.html Ajax (method).

    :return: the sessions within the supplied date range
    """

    activity_type_id = flask.request.json.get("activity_type_id", None)
    start_date = flask.request.json.get("start_date")
    end_date = flask.request.json.get("end_date")  # note: exclusive

    sessions = adf.return_activities_between_dates_of_activity_type(start_date, end_date,
                                                                    activity_type_id=activity_type_id)
    data = list()
    for session in sessions:
        data.append(dict(id=session.activity_id,
                         name=session.session_type.session_type_name.title(),
                         description=session.session_type.description,
                         facility_id=session.facility.facility_id,
                         facility_name=session.facility.name.title(),
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
    redirect_route = "/activities/booking"
    need_to_flash = False

    id = flask.request.json.get("id")
    session = adf.return_activity_with_id(id)

    user, response, has_cookie = cl.return_user_response(flask.request, True)

    # ----- Error Checking ----- #
    if user is None:
        flask.flash("You need to login to view session details.", "error")  # TODO: Does this make sense?
        need_to_flash = True
        status_code = 300  # redirect
        redirect_route = "/account/login"

    if not session:
        flask.flash("This session does not exist.", "error")  # TODO: Severe error
        need_to_flash = True
        status_code = 404

    # ----- Retrieve data ----- #
    total_bookings = len(tdf.return_bookings_with_activity_id(session.activity_id))
    spaces_left = session.session_type.maximum_activity_capacity - total_bookings
    duration: datetime.timedelta = session.end_time - session.start_time
    session_price = (duration.seconds // 3600 * session.session_type.hourly_activity_price)  # TODO: Bad #135

    subtotal = session_price

    session_dict = dict(
        user_role=None if user is None else user.__mapper_args__['polymorphic_identity'],
        minimum_age=session.session_type.minimum_age,
        spaces_left=spaces_left,
        session_price=round(session_price, 2),  # TODO: Bad #135
        subtotal=round(subtotal, 2),  # TODO: Bad #135
        max_booking=min(spaces_left, 8),
        num_weeks_available=adf.return_activity_weeks_available(id),

        status_code=status_code,
        redirect_route=redirect_route,
        flash=need_to_flash
    )

    # TODO: #135: Don't use floating point numbers for monetary calculation
    if type(user) is Manager:
        # TODO: Bad #135
        activity_income = total_bookings * session.session_type.hourly_activity_price * (
                          session.end_time - session.start_time).seconds // 3600
        activity_cost = total_bookings * session.session_type.hourly_activity_cost * (
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
            subtotal = session_price * (1 - membership_type.discount / float(100))  # TODO: Bad #135

            session_dict.update(dict(
                subtotal=round(subtotal, 2),  # TODO: Bad #135
                membership_name=membership_type.name.title(),
                membership_discount=membership_type.discount
            ))

    # Don't check here. Check in js; also don't return sessions before today's date FOR CUSTOMER.
    # if a CUSTOMER clicks on an EXPIRED session, show that it's expired, and don't allow user to book the session
    # note that EMPLOYEE and MANAGER **CAN** still view the event details)
    # if activity.start_time < datetime.datetime.now() and type(user) is Customer:
    #     return flask.abort(404)

    response = flask.make_response(json.dumps(session_dict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
