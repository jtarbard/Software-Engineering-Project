import flask
from main.data.db_classes.employee_data_db_class import Facility
blueprint = flask.Blueprint("info", __name__)


@blueprint.route('/info/about', methods=["GET"])
def about_func():
    return flask.render_template("/info/about.html")


@blueprint.route('/info/facilities', methods=["GET"])
def facilities_func():
    return flask.render_template("info/facilities.html",
                                 facilities=Facility.query.all())


@blueprint.route('/info/memberships', methods=["GET"])
def membership_func():
    return flask.render_template("info/memberships.html", page_title="Memberships")