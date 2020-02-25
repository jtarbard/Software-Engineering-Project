import flask

blueprint = flask.Blueprint("misc", __name__)


# Returns a 'not found' page if the route cannot be established
@blueprint.errorhandler(404)
def page_not_found(Error):
    return flask.render_template('/misc/not_found.html', has_cookie=True, nav=False, footer=False), 404


@blueprint.errorhandler(405)
def page_not_found(Error):
    return flask.render_template('/misc/not_found.html', has_cookie=True, nav=False, footer=False), 405


# Returns a 'server error' page if an error occurs
@blueprint.errorhandler(500)
def page_not_found(Error):
    return flask.render_template('/misc/server_error.html', has_cookie=True, nav=False, footer=False), 500
