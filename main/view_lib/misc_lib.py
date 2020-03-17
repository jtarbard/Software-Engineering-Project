import flask


# [Lewis S]
# Error handling function for dealing with server errors (Error: 500)
def page_error(error):
    return flask.render_template('/misc/server_error.html', has_cookie=True, nav=False, footer=False), 500


# [Lewis S]
# Error handling function for dealing with page not found errors (Error: 404 and 405)
def page_not_found(error):
    return flask.render_template('/misc/not_found.html', has_cookie=True, nav=False, footer=False), 404