import flask
import main.data.transactions.user_db_transaction as udf

blueprint = flask.Blueprint("index", __name__)

@blueprint.route("/")
def index_func():
    account_id = udf.check_valid_account_cookie(flask.request)  # Returns user ID from cookie
    user = None
    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)
            return response

    return flask.render_template("/index/index.html", User=user)

