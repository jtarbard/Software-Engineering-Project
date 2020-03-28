import flask
import main.view_lib.cookie_lib as cl

blueprint = flask.Blueprint("index", __name__)


@blueprint.route("/")
def index_func():
    user, response, has_cookie = cl.return_user_response(flask.request, False)
    return flask.render_template("/index/index.html", User=user, has_cookie=has_cookie)

