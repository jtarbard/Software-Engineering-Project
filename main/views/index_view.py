import flask
import main.view_lib.cookie_lib as cl
import datetime

blueprint = flask.Blueprint("index", __name__)


@blueprint.route("/")
def index_func():
    user, response, has_cookie = cl.return_user_response(flask.request, False)

    date_time = int(datetime.datetime.utcnow().strftime("%H"))

    return flask.render_template("/index/index.html", User=user, date_time=date_time, has_cookie=has_cookie)

