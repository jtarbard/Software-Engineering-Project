import flask
from main.data.db_classes.employee_data_db_class import Facility
from main.data.db_session import create_session
blueprint = flask.Blueprint("info", __name__)


@blueprint.route('/about')
def about():
    return flask.render_template("/info/about.html")


@blueprint.route('/facilities')
def facilities():
    session = create_session()
    return flask.render_template("info/facilities.html",
                                 facilities= session.query(Facility).all())


@blueprint.route('/membership')
def membership():
    return flask.render_template("info/memberships.html")
