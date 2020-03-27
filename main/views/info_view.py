import flask
import main.view_lib.cookie_lib as cl
import main.data.transactions.transaction_db_transaction as db_transaction
from main.data.db_classes.activity_db_class import Facility
from main.data.db_classes.user_db_class import Customer
from main.data.db_classes.transaction_db_class import MembershipType
from main.data.db_session import add_to_database

blueprint = flask.Blueprint("info", __name__)


@blueprint.route('/info/about', methods=["GET"])
def about_func():
    user, response = cl.return_user_response(flask.request, False)
    return flask.render_template("/info/about.html", page_title="About", User=user)


@blueprint.route('/info/contact_us', methods=["GET"])
def contact_us_view():
    user, response = cl.return_user_response(flask.request, False)
    return flask.render_template("/info/contact_us.html", User=user)


@blueprint.route('/info/facilities', methods=["GET"])
def facilities_view():
    user, response = cl.return_user_response(flask.request, False)
    return flask.render_template("info/facilities.html",
                                 facilities=Facility.query.all(), page_title="Facilities", User=user)


@blueprint.route('/info/memberships', methods=["GET"])
def membership_view():
    user, response = cl.return_user_response(flask.request, False)
    standard_id = 1
    premium_id = 2
    standard_price = MembershipType.query.filter_by(membership_type_id=standard_id).first().monthly_price
    premium_price = MembershipType.query.filter_by(membership_type_id=premium_id).first().monthly_price

    return flask.render_template("info/memberships.html", page_title="Memberships",
                                 User=user,premium_price=premium_price,standard_price=standard_price,
                                 standard_id=standard_id,premium_id=premium_id)


@blueprint.route("/info/memberships/buy", methods=["POST"])
def buy_membership():
    user, response = cl.return_user_response(flask.request, True)
    if response:
        return response

    membership_id = int(flask.request.form.get('buy_membership'))
    membership_duration = int(flask.request.form.get('membership_duration'))
    if membership_id is None:
        return flask.redirect("/info/memberships")

    is_valid, basket_activities, basket_membership, basket_membership_duration = \
        db_transaction.return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)

    if not is_valid:
        return cl.destroy_account_cookie(flask.redirect("/"))

    new_membership_type = db_transaction.return_membership_type_with_id(membership_id)
    response = cl.add_activity_or_membership_to_basket(
        new_membership_type, flask.request, duration = membership_duration)
    return response


@blueprint.route("/info/memberships/cancel", methods=["GET"])
def cancel_membership():
    user, response = cl.return_user_response(flask.request, True)
    if response:
        return response

    if type(user) is Customer:
        customer = Customer.query.filter_by(user_id=user.user_id).first()
        customer.current_membership = None
        add_to_database(customer)

    return flask.redirect("/account/your_account")
