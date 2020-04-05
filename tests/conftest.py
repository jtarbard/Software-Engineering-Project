import pytest
import os
import datetime
import re

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
    """ called before ``pytest_runtest_call(item). """
    import tests.helper.database_creation as creation
    creation.create_all()


# Automatically run for every test.
# Rolls the database back to the initial state (empty) so each test database is independent.
@pytest.yield_fixture(scope="function", autouse=True)
def db_setup_rollback():
    database.session.begin_nested()
    yield
    database.session.rollback()


@pytest.yield_fixture(scope='session')
def app():
    local_app = flask.Flask("main.app", instance_relative_config=True)
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
def template_checker():

    def _template_checker(**kwargs):
        response = kwargs.get("response", None)
        request = kwargs.get("request", None)
        templates = kwargs.get("templates", None)
        exp_status_code = kwargs.get("exp_status_code", 200)
        exp_title = kwargs.get("exp_title", None)
        exp_url = kwargs.get("exp_url", None)
        exp_template_path = kwargs.get("exp_template_path", None)
        exp_template_context: dict = kwargs.get("exp_template_context", {})
        exp_exist_cookies: list = kwargs.get("exp_exist_cookies", [])
        exp_non_exist_cookies: list = kwargs.get("exp_non_exist_cookies", [])

        soup = BeautifulSoup(response.data, 'html.parser')

        assert response.status_code == exp_status_code, "Invalid status code"
        assert request.path == exp_url, "Mismatching url (usually this indicates wrong redirection)"
        assert len(templates) == 1, "Returned not enough / too many templates. Expected 1 (This should never happen in theory)"
        template, context = templates[0]
        assert exp_title in soup.title.string or exp_title in context.get("page_title", ""), "Expected title not found"
        assert template.name == exp_template_path, "Rendered wrong template"
        # pythonic :)
        assert \
            all([ any([ context.get(exp_key, "") == val for val in exp_val ]) if type(exp_val) == list
                  else context.get(exp_key, "") == exp_val
                  for (exp_key, exp_val) in exp_template_context.items()
                ]), "Template rendered with wrong parameters. Expected:\n" + str(exp_template_context) + "\nActual:\n" + str(context)
        assert all([ (cookie in exp_exist_cookies) for cookie in request.cookies ]), "Some existing cookies should not exist"
        assert all([ (out_cookie not in request.cookies) for out_cookie in exp_non_exist_cookies ]), "Expected non-existent cookies exist"

        return context

    return _template_checker
