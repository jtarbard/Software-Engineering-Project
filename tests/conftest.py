import pytest
import os
import datetime
import re
from pprint import pprint

from bs4 import BeautifulSoup

import flask
from flask_sqlalchemy import SQLAlchemy
from main.app import register_blueprints, create_logging
from main.data.db_session import test_init, database

from main.data.db_classes.user_db_class import Customer, Employee, Manager

# What are the proper uses of conftest.py
# https://stackoverflow.com/questions/34466027/in-pytest-what-is-the-use-of-conftest-py-files


# TODO: Investigate what a hook is... https://pytest.org/en/latest/reference.html#hook-reference
def pytest_runtest_setup(item):
    import main.helper_functions.test_helpers.database_creation as creation
    creation.create_all()


# Automatically run for every test.
# Rolls the database back to the initial state (empty) so each test database is independent.
@pytest.yield_fixture(scope="function", autouse=True)
def db_setup_rollback(test_client):
    database.session.begin_nested()
    yield
    test_client.delete_cookie("localhost", "vertex_basket_cookie")
    test_client.delete_cookie("localhost", "vertex_account_cookie")
    database.session.rollback()



@pytest.yield_fixture(scope='session')
def app():
    local_app = flask.Flask("main.app", instance_relative_config=True)
    local_app.secret_key = "it's everyday bro"
    # configure
    # TODO: Change actual persisting file to tempfiles
    create_logging(local_app, transaction_filename="test_transactions.log", server_error_filename="test_server_error.log")
    register_blueprints(local_app)
    import main.view_lib.misc_lib as ml
    local_app.register_error_handler(404, ml.page_not_found)
    local_app.register_error_handler(405, ml.page_not_found)
    local_app.register_error_handler(500, ml.page_error)
    # QRcode(app)

    # with Postgresql() as postgresql:
    local_app.config['DEBUG'] = True
    local_app.config['TESTING'] = True
    # local_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    local_app.config['ENV'] = 'test'
    # local_app.config['SERVER_NAME'] = 'localhost'
    local_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # local_app.config['SQLALCHEMY_DATABASE_URI'] = postgresql.url()
    # ctx = local_app.app_context()
    # "With this you can access the request, g and session objects like in view functions." - https://flask.palletsprojects.com/en/1.1.x/testing/#the-first-test
    ctx = local_app.test_request_context()
    ctx.push()
    # local_app.preprocess_request()

    # create_all() inside
    test_init(local_app)

    yield local_app

    # database.session.rollback()
    database.drop_all()

    ctx.pop()


@pytest.yield_fixture(scope='function')
def test_client(app):
    with app.test_client(use_cookies=True) as tc:  # THIS WAS THE PROBLEM ALL ALONG OH MY GOD
        yield tc


@pytest.fixture(scope="function")
def populate_database():
    from main.helper_functions.test_helpers.database_creation import membership_type_objs, \
        receipt_for_membership_objs, customer_with_membership_objs, membership_objs, \
        activity_type_objs, activity_objs, facility_objs, customer_objs, employee_objs, manager_objs

    def _add(tables_to_populate: list):
        table_dict = {"facility": facility_objs,
                      "membership_type": membership_type_objs,
                      "activity_type": activity_type_objs,
                      "activity": activity_objs,
                      "customer": customer_objs,
                      # TODO: Bundle the following 3 into 1. Add customer first, then receipt, then membership
                      "customer_with_membership": customer_with_membership_objs,
                      "membership": membership_objs,
                      "membership_receipt": receipt_for_membership_objs,
                      "employee": employee_objs,
                      "manager": manager_objs
                      }

        for table in [table for table in tables_to_populate if (table in table_dict.keys())]:
            for obj in table_dict[table]:
                database.session.add(obj)

        database.session.flush()

    return _add


@pytest.fixture(scope="function")
def template_checker():

    def _template_checker(**kwargs):
        response = kwargs.get("response", None)
        request = kwargs.get("request", None)
        templates = kwargs.get("templates", None)
        flash_messages = kwargs.get("flash_messages", None)

        exp_status_code = kwargs.get("exp_status_code", 200)
        exp_title = kwargs.get("exp_title", "")
        exp_url = kwargs.get("exp_url", None)
        exp_template_path = kwargs.get("exp_template_path", None)
        exp_template_context: dict = kwargs.get("exp_template_context", dict())

        exp_flash_message = kwargs.get("exp_flash_message", "")
        exp_flash_category = kwargs.get("exp_flash_category", "")

        exp_exist_cookies: list = kwargs.get("exp_exist_cookies", list())
        exp_cookie_values: dict = kwargs.get("exp_cookie_values", dict())

        exp_text: list = kwargs.get("exp_text", list())
        exp_args: dict = kwargs.get("exp_args", dict())

        soup = BeautifulSoup(response.data, 'html.parser')

        assert response.status_code == exp_status_code, \
            "Invalid status code"
        for (arg_name, arg_val) in exp_args:
            assert arg_name in response.args.keys(), \
                f"Url does not have the argument {arg_name}"
            assert arg_val == response.args.get(arg_name, None), \
                f"{arg_name} argument expected to be {arg_val} but got {response.args.get(arg_name, None)}"

        template, context = templates[0]
        print("Context obtained:")
        pprint(context)
        assert request.path == exp_url, \
            "Mismatching url (usually this indicates wrong redirection)"
        assert len(templates) == 1, \
            "Returned not enough / too many templates. Expected 1 (This should never happen in theory)"
        assert exp_title in soup.title.string or exp_title in context.get("page_title", ""), \
            "Expected title not found"
        assert template.name == exp_template_path, \
            "Rendered wrong template"
        # pythonic :)
        assert \
            all([ any([ context.get(exp_key, "") == val for val in exp_val ]) if type(exp_val) == list
                  else context.get(exp_key, "") == exp_val
                  for (exp_key, exp_val) in exp_template_context.items()
                ]), \
            "Template rendered with wrong parameters. Expected:\n" + str(exp_template_context) + \
            "\nActual:\n" + str(context)

        for text in exp_text:
            assert text.lower() in soup.get_text().lower()

        message, category = None, None
        if exp_flash_message != "" or exp_flash_category != "":
            assert len(flash_messages) == 1, \
                "Did not flash message" if len(flash_messages) == 0 else "Flashed too many messages"
            message, category = flash_messages[0]
            print("Flash message obtained:")
            print("Message:", message)
            print("Category:", category)
            assert category == exp_flash_category, \
                f"Expected category to be {exp_flash_category}, but got {category}"
            assert exp_flash_message.lower() in message.lower(), \
                f"Expected {exp_flash_message.lower()} to be in {message.lower()}"

        print("Cookies:")
        pprint(request.cookies)
        assert all([ (cookie in exp_exist_cookies) for cookie in request.cookies ]), \
            "Some existing cookies should not exist: " + str(request.cookies)
        assert all([ request.cookies[key] == val for (key, val) in exp_cookie_values.items() ]), \
            "Some cookies have unexpected values. Actual: " + str(request.cookies) + ", expected: " + str(exp_cookie_values)

        return context, message, category

    return _template_checker


@pytest.fixture(scope="function")
def basket_template_checker(template_checker):

    def _basket_template_checker(**kwargs):
        exp_activities: dict = kwargs.get("exp_activities", dict())
        exp_membership = kwargs.get("exp_membership", None)
        exp_basket_membership_duration = kwargs.get("exp_basket_membership_duration", None)
        exp_membership_discount = kwargs.get("exp_membership_discount", 0)
        exp_total_activity_price = kwargs.get("exp_total_activity_price", 0)
        exp_total_discounted_price = kwargs.get("exp_total_discounted_price", 0)
        exp_final_price = kwargs.get("exp_final_price", 0)

        context, message, category = template_checker(**kwargs)

        assert all( actual_activity in list(exp_activities.keys()) for actual_activity in context.get("basket_activities", []) ), \
            "Found unexpected activitiies in rendered page"
        assert context.get("basket_membership", None) == exp_membership, \
            "Mismatching basket_membership"
        assert context.get("basket_membership_duration", None) == exp_basket_membership_duration, \
            "Mismatching basket_membership_duration"
        assert context.get("current_membership_discount", 0) == exp_membership_discount, \
            "Mismatching current_membership_discount"
        assert context.get("total_activity_price", 0) == exp_total_activity_price, \
            "Mismatching total_activity_price"
        assert context.get("total_discounted_price", 0) == exp_total_discounted_price, \
            "Mismatching total_discounted_price"
        for ctx_activity_obj, (session_price, num_bookings, bulk_discount) in context.get("activity_and_price", dict()).items():
            assert ctx_activity_obj in exp_activities, \
                "Rendered with an unexpected activity in activity_and_price"
            exp_session_price, exp_num_bookings, exp_bulk_discount = exp_activities.get(ctx_activity_obj, (None, None, None))
            assert session_price == exp_session_price, \
                "Mismatching session_price for activity " + str(ctx_activity_obj)
            assert num_bookings == exp_num_bookings, \
                "Mismatching num_bookings for activity " + str(ctx_activity_obj)
            assert bulk_discount == exp_bulk_discount, \
                "Mismatching bulk_discount for activity " + str(ctx_activity_obj)
        assert context.get("final_price", 0) == exp_final_price, \
            "Mismatching final_price"

    return _basket_template_checker


@pytest.fixture(scope="function")
def generic_route_test(app, test_client, mocker, template_checker, populate_database):
    """
    Generic test for routes.
    :param request_type: "POST" or "GET"
    :param data: basic actual & expected data, returned from the test_route GET request
    :param extra_exp_data: extra data expected from the test_route GET request
    :param post_data: data to pass in POST request

    :param app: fixture
    :param test_client:  fixture
    :param mocker: pytest supplied fixture
    :param template_checker: fixture
    :param populate_database: fixture
    :return: None
    """

    def _generic_route_test(request_type: str, data: dict, extra_exp_data: dict = {}, post_data: dict = {}):
        import main.helper_functions.test_helpers.flask_signal_capturer as signal_capturer
        import main.helper_functions.test_helpers.mocked_functions as mocked_functions

        database_tables = data.get("database_tables", [])
        test_route = data.get("test_route", "/")

        mocked_return_user_response = data.get("mocked_return_user_response")
        create_basket_cookie, basket_cookie_value = data.get("create_basket_cookie_and_value",
                                                             (False, ""))
        create_account_cookie, account_cookie_value = data.get("create_account_cookie_and_value",
                                                               (True, "Account"))

        exp_status_code = data.get("exp_status_code", 200)
        exp_title = data.get("exp_title")
        exp_url = data.get("exp_url")
        exp_template_path = data.get("exp_template_path")

        exp_flash_message = data.get("exp_flash_message", "")
        exp_flash_category = data.get("exp_flash_category", "")

        exp_exist_cookies = data.get("exp_exist_cookies", list())
        exp_cookie_values = data.get("exp_cookie_values", dict())

        exp_text = data.get("exp_text", [])
        exp_args = data.get("exp_args", [])

        # ------------------------------------------------------- #

        # Get objects after database is populated (and they are created)
        mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=mocked_return_user_response)
        # Do not commit any database change
        mocker.patch("main.data.db_session.add_to_database", side_effect=mocked_functions.add_to_database)
        mocker.patch("main.data.db_session.add_to_database", side_effect=mocked_functions.delete_from_database)
        # Populate database with simple dummy data
        populate_database(database_tables)

        # ------------------------------------------------------- #

        with signal_capturer.captured_templates(app) as templates:
            with signal_capturer.captured_flashes(app) as flash_messages:

                # TODO: Generalize
                if create_basket_cookie:
                    test_client.set_cookie("localhost", "vertex_basket_cookie", basket_cookie_value)
                if create_account_cookie:
                    test_client.set_cookie("localhost", "vertex_account_cookie", account_cookie_value)

                if request_type.upper() == "POST":
                    rv = test_client.post(test_route, follow_redirects=True, data=post_data)
                elif request_type.upper() == "GET":
                    rv = test_client.get(test_route, follow_redirects=True)
                else:
                    assert False, f"Invalid request type \"{request_type}\". Can only be \"POST\" or \"GET\"."

                context, message, category = template_checker(response=rv, request=flask.request, templates=templates,
                                                              flash_messages=flash_messages,
                                                              exp_title=exp_title,
                                                              exp_url=exp_url, exp_template_path=exp_template_path,
                                                              exp_flash_message=exp_flash_message, exp_flash_category=exp_flash_category,
                                                              exp_exist_cookies=exp_exist_cookies,
                                                              exp_cookie_values=exp_cookie_values,
                                                              exp_status_code=exp_status_code,
                                                              exp_text=exp_text,
                                                              exp_args=exp_args)

                for (key, val) in extra_exp_data.items():
                    assert context.get(key, None) == val, \
                        f"Expected {key} to be {val} but got {context.get(key, None)}"

        # --------------------------------- END OF THIS TEST: _generic_route_test --------------------------------- #

    return _generic_route_test


@pytest.fixture
def generic_route_data():
    """
    Generic_Route_Test
    GIVEN a Flask application
    WHEN the <supplied_url> page is requested (GET)
    VARYING CONDITIONS 1. User with/without membership is logged in / not logged in
    THEN check 1. Valid status code (200)
               2. The redirected url
               3. page_title (rendered template parameter) or actual page title
               4. name of the rendered template
               5. Existing cookies

    DATA for generic GET rule.
    This is meant to be extended.
    """

    def _generic_route_data(request, exp_title, exp_url, exp_template_path, exp_args=dict(), needs_login=True):
        from main.helper_functions.test_helpers.mocked_functions import return_customer_no_membership_with_no_response, \
            return_customer_premium_with_no_response, \
            return_customer_standard_with_no_response, \
            return_not_logged_in_user_response, return_not_logged_in_user_with_no_response

        # TODO: Consider refactoring the data in another function so that "data" doesn't need to be re-run n times.
        #       Have 2 functions as "Data Container" and "Data Retrieval"

        # -----------------------------------------| ============= |----------------------------------------- #
        # -----------------------------------------|  Basic Tests  |----------------------------------------- #
        # -----------------------------------------| ============= |----------------------------------------- #

        # Test 0
        # Not logged in, No membership
        # ------
        # 1. vertex_account_cookie does NOT exist
        if request.param == 0:
            return {"mocked_return_user_response": return_not_logged_in_user_response if needs_login
                                                   else return_not_logged_in_user_with_no_response,
                    "create_basket_cookie_and_value": (False, ""),
                    "create_account_cookie_and_value": (False, ""),

                    "exp_title": exp_title, "exp_url": exp_url,
                    "exp_template_path": exp_template_path,
                    "exp_args": exp_args,
                    "exp_exist_cookies": []}

        # Test 1
        # Logged in, No membership
        # ------
        # 1. vertex_account_cookie exists
        # 2. User does not have a membership
        elif request.param == 1:
            return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                    "create_basket_cookie_and_value": (False, ""),
                    "create_account_cookie_and_value": (True, "Account"),

                    "exp_title": exp_title, "exp_url": exp_url,
                    "exp_template_path": exp_template_path,
                    "exp_args": exp_args,
                    "exp_exist_cookies": ["vertex_account_cookie"]}

        # Test 2
        # Logged in, standard membership
        # ------
        # 1. vertex_account_cookie exists
        # 2. User has standard membership
        elif request.param == 2:
            return {"mocked_return_user_response": return_customer_standard_with_no_response,
                    "create_basket_cookie_and_value": (False, ""),
                    "create_account_cookie_and_value": (True, "Account"),

                    "exp_title": exp_title, "exp_url": exp_url,
                    "exp_template_path": exp_template_path,
                    "exp_args": exp_args,
                    "exp_exist_cookies": ["vertex_account_cookie"]}

        # Test 3
        # Logged in, premium membership
        # ------
        # 1. vertex_account_cookie exists
        # 2. User has premium membership
        elif request.param == 3:
            return {"mocked_return_user_response": return_customer_premium_with_no_response,
                    "create_basket_cookie_and_value": (False, ""),
                    "create_account_cookie_and_value": (True, "Account"),

                    "exp_title": exp_title, "exp_url": exp_url,
                    "exp_template_path": exp_template_path,
                    "exp_args": exp_args,
                    "exp_exist_cookies": ["vertex_account_cookie"]}

        # -----------------------------------------/ ============= \----------------------------------------- #
        # ----------------------------------------| - Extra Tests - |---------------------------------------- #
        # -----------------------------------------\ ============= /----------------------------------------- #

        # Test 4
        # Basket cookie is retained and unmodified
        # ------
        # 1. vertex_account_cookie exists
        # 2. User does not have a membership
        # 3. Basket cookie exists
        elif request.param == 4:
            return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                    "create_basket_cookie_and_value": (True, "A:1;M:1:1"),
                    "create_account_cookie_and_value": (True, "Account"),

                    "exp_title": exp_title, "exp_url": exp_url,
                    "exp_template_path": exp_template_path,
                    "exp_args": exp_args,
                    "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"],
                    "exp_cookie_values": {"vertex_basket_cookie": "A:1;M:1:1"}}

        else:
            return False

    return _generic_route_data
