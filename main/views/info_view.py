import flask
from main.data.db_classes.activity_db_class import Facility
blueprint = flask.Blueprint("info", __name__)


@blueprint.route('/about')
def about():
    return flask.render_template("/info/about.html")


@blueprint.route('/facilities')
def facilities():
    return flask.render_template("info/facilities.html",
                                 facilities=Facility.query.all())


@blueprint.route('/membership')
def membership():
    return flask.render_template("info/memberships.html")
