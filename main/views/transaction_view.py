import flask

blueprint = flask.Blueprint("transaction", __name__)


@blueprint.route("/payments")
def payments():
    return flask.render_template("transactions/payments.html")


@blueprint.route("/payments/receipt")
def receipt():
    return flask.render_template("transactions/receipt.html")
