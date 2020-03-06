import flask
import main.cookie_transaction as ct
import main.data.transactions.user_db_transaction as udf
from main.data.db_classes.activity_db_class import Facility
blueprint = flask.Blueprint("info", __name__)


@blueprint.route('/info/about', methods=["GET"])
def about_func():
    user, response = ct.return_user_response(flask.request, False)
    return flask.render_template("/info/about.html", User=user)


@blueprint.route('/info/facilities', methods=["GET"])
def facilities_func():
    user, response = ct.return_user_response(flask.request, False)
    return flask.render_template("info/facilities.html",
                                 facilities=Facility.query.all(), User=user)


@blueprint.route('/info/memberships', methods=["GET"])
def membership_func():
    user, response = ct.return_user_response(flask.request, False)
    return flask.render_template("info/memberships.html", page_title="Memberships", User=user)

@blueprint.route('/info/facilities/facilities_info', methods=["GET"])
def facilities_info_func():
    user, response = ct.return_user_response(flask.request, False)
    return flask.render_template("info/facilities_info.html",
                                 facilities=Facility.query.all(), User=user)