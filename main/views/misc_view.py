import flask

blueprint = flask.Blueprint("misc", __name__)


@blueprint.route("/test/test_page")
def test_page():
    return flask.render_template("/misc/test_page.html")

