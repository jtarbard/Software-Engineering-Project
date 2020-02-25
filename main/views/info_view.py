import flask

blueprint = flask.Blueprint("info", __name__)


@blueprint.route("/info/memberships", methods=["GET"])
def membership_func():
    return flask.render_template("/info/memberships.html")
