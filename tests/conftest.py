import pytest
import os
import datetime
import re

from bs4 import BeautifulSoup

import flask
from flask_sqlalchemy import SQLAlchemy
from main.app import register_blueprints
from main.data.db_session import test_init

from main.data.db_classes.user_db_class import Customer, Employee, Manager

# What are the proper uses of conftest.py
# https://stackoverflow.com/questions/34466027/in-pytest-what-is-the-use-of-conftest-py-files


# TODO: Investigate what a hook is... https://pytest.org/en/latest/reference.html#hook-reference
def pytest_runtest_setup(item):
    """ called before ``pytest_runtest_call(item). """


# www.stackoverflow.com/questions/44677426/can-i-pass-arguments-to-pytest-fixtures
@pytest.fixture(scope='module')
def new_user():
    """
    Tests Customer, Employee, and Manager classes
    :return: an object of the appropriate class, with the supplied parameters
    """
    titles = ["Mr", "Mr", "Mrs"]
    passwords = ["passw0rD", "oai9*(13jiovn__eiqf9OIJqlk", "Admin666"]
    first_names = ["John", "FIRSTNAME", "jane"]
    last_names = ["Doe", "LASTNAME", "doe"]
    emails = ["johndoe@thevertex.com", "notsurewhattoexpect@but.hereyougo", "JANEDOE@GMAIL.COM"]
    tels = ["01685469958", "13854685599", "99999999999"]
    bdays = [datetime.datetime(1960, 1, 1), datetime.datetime(1975, 1, 4), datetime.datetime(2004, 3, 22)]
    postcodes = ["W1A 0AX", "DN55 1PT", "EC1A 1BB"]
    addresses = ["3 Clos Waun Wen, Morriston", "The Old Mill, Llwyngwril", "14 Gwyn Drive, Caerphilly"]
    countries = ["GB", "US", "CN"]

    def _create_user(user_type):
        if user_type.lower() == 'customer':
            i = 0
            return Customer(title=titles[i], password=passwords[i], first_name=first_names[i],
                            last_name=last_names[i], email=emails[i], tel_number=tels[i],
                            dob=bdays[i], postal_code=postcodes[i], address=addresses[i], country=countries[i])
        elif user_type.lower() == 'employee':
            i = 1
            return Employee(title=titles[i], password=passwords[i], first_name=first_names[i],
                            last_name=last_names[i], email=emails[i], tel_number=tels[i],
                            dob=bdays[i], postal_code=postcodes[i], address=addresses[i], country=countries[i])
        elif user_type.lower() == 'manager':
            i = 2
            return Manager(title=titles[i], password=passwords[i], first_name=first_names[i],
                           last_name=last_names[i], email=emails[i], tel_number=tels[i],
                           dob=bdays[i], postal_code=postcodes[i], address=addresses[i], country=countries[i])
        else:
            raise Exception(f"[TESTING: conftest.py > new_user()] Unknown user type {user_type}")

    return _create_user


@pytest.yield_fixture(scope='session')
def app():
    local_app = flask.Flask("main.app", instance_relative_config=True)
    # configure
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

    test_init(local_app)

    yield local_app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def test_client(app):
    with app.test_client(use_cookies=True) as tc:  # THIS WAS THE PROBLEM ALL ALONG OH MY GOD
        yield tc


@pytest.yield_fixture(scope='session')
def db(app):
    database = SQLAlchemy(app)
    # database.app = app
    database.create_all()

    yield database

    database.session.remove()
    database.drop_all()


# For pytest-flask-sqlalchemy. Caused (a lot) more problems than needed.
# @pytest.fixture(scope='session')
# def _db(db):
#     """
#     Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
#     database connection.
#     """
#     return db


# https://stackoverflow.com/questions/23987564/test-flask-render-template-context
from flask import template_rendered
from contextlib import contextmanager

@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture(scope='session')
def page_title_dict():
    # Current working directory = main/..
    dictionary = {}

    for root, dirs, files in os.walk(os.getcwd()):
        for file in [f for f in files if f.endswith(".html")]:
            with open(root + "\\" + file, "r", encoding='utf-8') as content:
                title = ""
                is_title_portion = False  # this doesn't matter
                for line in content.readlines():
                    # Remove ALL white space and new line
                    cleansed_line = line.replace("\n", "").replace(" ", "")
                    # Remove comments
                    cleansed_line = re.sub("(<!--.*?-->)", "", cleansed_line, flags=re.DOTALL)

                    if cleansed_line == "{%blocktitle%}":
                        is_title_portion = True
                    elif cleansed_line == "{%endblock%}" and is_title_portion:
                        dictionary[file] = title
                        break  # finish reading title. Read the next file
                    elif is_title_portion:
                        title += line + ("\n" if title != "" else "")
                if not dictionary.get(file, False):
                    dictionary[file] = "No Title"
    return dictionary


# TODO: Maybe use parametrize from pytest?
@pytest.fixture(scope="function")
def template_checker():

    def _template_checker(**kwargs):
        response = kwargs.get("response", None)
        request = kwargs.get("request", None)
        templates = kwargs.get("templates", None)
        exp_title = kwargs.get("exp_title", None)
        exp_template_path = kwargs.get("exp_template_path", None)
        exp_in_cookies: list = kwargs.get("exp_in_cookies", None)
        exp_out_cookies: list = kwargs.get("exp_out_cookies", None)

        soup = BeautifulSoup(response.data, 'html.parser')

        # assert rv.status_code == 200
        # assert "/account/login" == flask.request.path
        # assert len(templates) == 1
        # template, context = templates[0]
        # assert exp_title in soup.title.string or exp_title in context.get("page_title", "")
        # assert template.name == '/account/login_register.html'
        # assert len(flask.request.cookies) == 0


# Deprecated. But I would really like to still keep this as a backup solution
# def cookies(test_client_obj):
#     return vars(vars(test_client_obj).get("cookie_jar")).get("_cookies").get("localhost.local").get("/").keys()

