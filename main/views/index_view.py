import flask
import main.data.transactions.user_db_transaction as udf
import main.cookie_transaction as ct

blueprint = flask.Blueprint("index", __name__)


@blueprint.route("/")
def index_func():
    user, response = ct.return_user_response(flask.request, False)
    return flask.render_template("/index/index.html", User=user)

