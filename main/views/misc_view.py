import flask
import main.view_lib.cookie_lib as cl

blueprint = flask.Blueprint("misc", __name__)


@blueprint.route("/misc/policy_info")
def policy_info_view():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    return flask.render_template("/misc/policy_info.html", User=user, has_cookie=has_cookie)
