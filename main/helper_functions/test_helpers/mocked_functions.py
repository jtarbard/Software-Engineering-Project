import flask

from main.data.db_classes.user_db_class import User


def return_customer_no_membership_with_no_response(request, needs_login):
    from main.helper_functions.test_helpers.database_creation import customer_objs
    return User.query.filter_by(user_id=customer_objs[0].user_id).first(), None, True


def return_customer_standard_with_no_response(request, needs_login):
    from main.helper_functions.test_helpers.database_creation import customer_with_membership_objs
    return User.query.filter_by(user_id=customer_with_membership_objs[0].user_id).first(), None, True


def return_customer_premium_with_no_response(request, needs_login):
    from main.helper_functions.test_helpers.database_creation import customer_with_membership_objs
    return User.query.filter_by(user_id=customer_with_membership_objs[1].user_id).first(), None, True


def return_logged_in_user_response(request, needs_login):
    from main.helper_functions.test_helpers.database_creation import customer_objs
    return User.query.filter_by(user_id=customer_objs[0].user_id).first(), flask.redirect("/account/login"), True


def return_not_logged_in_user_response(request, needs_login):
    return False, flask.redirect("/account/login"), True


# Same as add_to_database but does not commit
def add_to_database(database_class):
    from main.data.db_session import database
    try:
        database.session.add(database_class)
        database.session.flush()
        return True
    except:
        return False


# Same as delete_from_database but does not commit
def delete_from_database(database_class):
    from main.data.db_session import database
    try:
        database.session.delete(database_class)
        database.session.flush()
        return True
    except:
        return False
