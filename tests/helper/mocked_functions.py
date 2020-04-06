import flask


def return_logged_in_user_response(request, needs_login):
    return True, flask.redirect("/account/login"), True  # TODO: return a real user instead of True


def return_not_logged_in_user_response(request, needs_login):
    return False, flask.redirect("/account/login"), True
