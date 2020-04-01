import flask
import datetime

import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.transaction_db_transaction as tdf
from main.data.db_classes.activity_db_class import Activity, ActivityType
from main.data.db_classes.transaction_db_class import Membership
from main.data.db_classes.user_db_class import Customer
import main.view_lib.cookie_lib as cl

blueprint = flask.Blueprint("activities", __name__)


@blueprint.route("/activities/types", methods=["POST", "GET"])
def view_activity_types():
    user, response = cl.return_user_response(flask.request, False)
    if response:
        return response

    if flask.request.method == "POST":
        data_form = flask.request.form
        activity = data_form.get("activity")
        amount = data_form.get("amount")

        if amount == "single":
            return flask.redirect(flask.url_for("activities.view_activities", _method='GET', multiple=False, sent_activity=activity))
        elif amount == "multiple":
            return flask.redirect(flask.url_for("activities.view_activities", _method='GET', multiple=True, sent_activity=activity))
    else:
        facilities = adf.return_facilities("Any")
        activity_types = adf.return_all_activity_types()

        return flask.render_template("/activities/activity_types.html", User=user,
                                     activity_types=activity_types, facilities=facilities, page_title="Activities")


@blueprint.route('/activities/view_activities', methods=["POST", "GET"], defaults={'multiple': False, 'sent_activity': 0})
@blueprint.route('/activities/<sent_activity>_<multiple>', methods=["POST", "GET"])
def view_activities(multiple, sent_activity: int):
    sent_activity = int(sent_activity)

    user, response = cl.return_user_response(flask.request, False)
    if response:
        return response

    data_form = flask.request.form

    bulk_activities = data_form.getlist("bulk_activity")

    is_valid, basket_activities, basket_membership, basket_membership_duration = \
        tdf.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if bulk_activities:

        if not is_valid:
            return cl.destroy_account_cookie(flask.redirect("/"))

        if basket_activities:
            if (basket_membership and len(basket_activities) > 14) or len(basket_activities) > 15:
                return flask.render_template("/misc/general_error.html", error="Basket full", User=user)

        try:
            activity_type = adf.return_activity_with_id(bulk_activities[0]).activity_type
        except:
            return flask.abort(500)

        added_activities = []
        for activity_id in bulk_activities:
            added_activity: Activity = adf.return_activity_with_id(activity_id)
            if not added_activity:
                return flask.abort(500)

            if activity_type != added_activity.activity_type:
                return flask.abort(500)

            if added_activity in added_activities:
                return flask.abort(500)

            added_activities.append(added_activity)
            spaces_left = activity_type.maximum_activity_capacity - len(
                tdf.return_bookings_with_activity_id(activity_id))

            if spaces_left <= 0:
                return flask.render_template("/misc/general_error.html", error="Not enough spaces left on activity",
                                             User=user)

        response = cl.add_activities(added_activities, flask.request)

        if not response:
            return flask.abort(500)

        bulk_activity_type = adf.return_activity_type_name_with_activity_type_id(sent_activity)
        flask.flash(bulk_activity_type.title() + " sessions have been added to your basket.", category="success")
        return response

    start_time = data_form.get("start_time")
    start_date = data_form.get("start_date")
    if type(start_date) is str:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    if type(start_time) is str:
        try:
            start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
        except:
            start_time = datetime.datetime.strptime(start_time, "%H:%M:%S").time()
    activity_type_id = data_form.get("activity")
    facility_id = data_form.get("facility")

    if not start_time:
        start_time = datetime.datetime.now().time()
    if not start_date:
        start_date = datetime.date.today()
    if not activity_type_id:
        activity_type_id = "Any"
    elif activity_type_id != "Any":
        activity_type_id = int(activity_type_id)
    if not facility_id:
        facility_id = "Any"
    elif facility_id != "Any":
        facility_id = int(facility_id)

    start_search = datetime.datetime.combine(start_date, start_time)

    if start_search < datetime.datetime.now():
        start_search = datetime.datetime.now()

    activity_types = adf.return_activity_types("Any")

    facilities = adf.return_facilities("Any")

    if not facilities or not activity_types:
        flask.abort(500)

    activity_dict = {}

    if (flask.request.method == "POST") or (flask.request.method == "GET" and sent_activity == 0):
        activity_list = adf.return_activities_between_dates_with_facility_and_activity(start_search, datetime.datetime.today() + datetime.timedelta(days=14),
                                                                                   activity_type_id=activity_type_id, facility_id=facility_id)
    else:
        activity_list = adf.return_activities_between_dates_with_facility_and_activity(start_search, datetime.datetime.today() + datetime.timedelta(days=14),
                                                                                    activity_type_id=sent_activity, facility_id=facility_id)

    for i, activity in enumerate(activity_list):
        activity_capacity = adf.return_activity_capacity_with_activity_type_id(activity.activity_type_id)
        if basket_activities:
            amount_in_basket = basket_activities.count(activity)
            if amount_in_basket >= 8:
                continue
        else:
            amount_in_basket = 0

        avaliability = (activity_capacity - len(tdf.return_bookings_with_activity_id(activity.activity_id)) - amount_in_basket)
        if avaliability <= 0:
            continue

        activity_dict[activity_list[i]] = avaliability

    search_field_data = {}
    search_field_data["start_date"] = start_date.strftime("%Y-%m-%d")
    search_field_data["min_date"] = datetime.date.today()
    search_field_data["max_date"] = datetime.date.today() + datetime.timedelta(days=14)
    if start_date == datetime.date.today():
        search_field_data["min_time"] = datetime.datetime.now().strftime("%H:00:00")
    else:
        search_field_data["min_time"] = datetime.datetime.now().strftime("00:00:00")
    search_field_data["from_time"] = start_time.strftime("%H:00:00")
    search_field_data["facility"] = facility_id
    search_field_data["activity"] = activity_type_id

    return flask.render_template("/activities/activities.html", User=user, activity_dict=activity_dict,
                                 activity_types=activity_types, facilities=facilities,
                                 search_field_data=search_field_data, multiple=multiple, sent_activity=sent_activity)


@blueprint.route("/activities/view_activity/<int:activity_id>", methods=["GET"])
def view_activity(activity_id: int):
    user, response = cl.return_user_response(flask.request, True)
    if response:
        return response

    activity = adf.return_activity_with_id(activity_id)
    if not activity:
        return flask.abort(404)

    spaces_left = activity.activity_type.maximum_activity_capacity - len(
        tdf.return_bookings_with_activity_id(activity.activity_id))

    if type(user) is not Customer or spaces_left <= 0:
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
        membership = Membership.query.filter_by(membership_id=membership.membership_id).first().membership_type
        final_price = session_price * (1 - membership.discount / float(100))

    return flask.render_template("/activities/activity.html", activity=activity, session_price=round(session_price, 2),
                                 spaces_left=spaces_left, membership=membership,
                                 final_price=round(final_price, 2), User=user, max_booking=min(spaces_left, 8))
