import flask
import main.view_lib.cookie_lib as cl

blueprint = flask.Blueprint("misc", __name__)


@blueprint.route("/misc/policy_info")
def policy_info():
    user, response = cl.return_user_response(flask.request, True)
    return flask.render_template("/misc/policy_info.html", User=user)

