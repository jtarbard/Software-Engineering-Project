import flask

blueprint = flask.Blueprint("index", __name__)

@blueprint.route("/")
def index_func():
    return flask.render_template("/index/index.html")

