import flask

def page_error(error):
    return flask.render_template('/misc/server_error.html', has_cookie=True, nav=False, footer=False), 500

def page_not_found(error):
    return flask.render_template('/misc/not_found.html', has_cookie=True, nav=False, footer=False), 404