import flask


def return_customer_no_membership_with_no_response(request, needs_login):
    from main.helper_functions.test_helpers.database_creation import customer_objs
    return customer_objs[0], None, True


def return_customer_standard_with_no_response(request, needs_login):
    from main.helper_functions.test_helpers.database_creation import customer_with_membership_objs
    return customer_with_membership_objs[0], None, True


def return_customer_premium_with_no_response(request, needs_login):
    from main.helper_functions.test_helpers.database_creation import customer_with_membership_objs
    return customer_with_membership_objs[1], None, True


def return_logged_in_user_response(request, needs_login):
    from main.helper_functions.test_helpers.database_creation import customer_objs
    return customer_objs[0], flask.redirect("/account/login"), True


def return_not_logged_in_user_response(request, needs_login):
    return False, flask.redirect("/account/login"), True