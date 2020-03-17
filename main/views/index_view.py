import flask
import main.view_lib.cookie_lib as cl

blueprint = flask.Blueprint("index", __name__)


@blueprint.route("/")
def index_func():
    user, response = cl.return_user_response(flask.request, False)
    return flask.render_template("/index/index.html", User=user)

