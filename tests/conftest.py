import pytest
import os
import datetime
import re
from flask_sqlalchemy import SQLAlchemy
from testing.postgresql import Postgresql
from main.app import create_app
# from main.data.db_session import database

from main.data.db_classes.user_db_class import Customer, Employee, Manager

TEST_DATABASE_URI = 'sqlite://'  # SQLite :memory: database

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
    local_app = create_app()
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
    ctx = local_app.test_request_context("/account/login")
    ctx.push()
    local_app.preprocess_request()

    yield local_app

    ctx.pop()


@pytest.fixture(scope='module')
def test_client(app):
    with app.test_client(use_cookies=True) as tc:  # THIS WAS THE PROBLEM ALL ALONG OH MY GOD
        yield tc


@pytest.yield_fixture(scope='session')
def db(app):
    datab = SQLAlchemy(app)
    # database.app = app
    datab.create_all()

    yield datab

    datab.drop_all()


# @pytest.fixture(scope='function')
# def session(db, new_user):
#     connection = db.engine.connect()
#     transaction = connection.begin()
#
#     options = dict(bind=connection, binds={})
#     this_session = db.create_scoped_session(options=options)
#
#     db.session = this_session
#     db.session.add(new_user("customer"))
#
#     yield this_session
#
#     transaction.rollback()
#     connection.close()
#     this_session.remove()


@pytest.fixture(scope='session')
def _db(db):
    """
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    """
    return db


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


# www.patricksoftwareblog.com/testing-a-flask-application-using-pytest
# @pytest.fixture(scope='session')
# def test_client():
#     # db_fd, app.config['DATABASE'] = tempfile.mkstemp()
#     app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
#
#     # Create the database
#     database = SQLAlchemy(app)
#     database.create_all()
#
#     connection = database.engine.connect()
#     transaction = connection.begin()
#
#     options = dict(bind=connection, binds={})
#     session = database.create_scoped_session(options=options)  # ? What options
#
#     database.session = session
#
#     # Flask provides a way to test your application by exposing the Werkzeug test Client
#     # and handling the context locals for you.
#     testing_client = app.test_client()
#
#     # Establish an application context before running the tests.
#     # "With this you can access the request, g and session objects like in view functions." - https://flask.palletsprojects.com/en/1.1.x/testing/#the-first-test
#     ctx = app.test_request_context()
#     ctx.push()
#
#     yield testing_client  # this is where the testing happens!
#
#     ctx.pop()
#
#     # clean database
#     database.drop_all()
#     transaction.rollback()
#     connection.close()
#     session.remove()
#     # os.close(db_fd)  # if used tempfile
#     # os.unlink(app.config['DATABASE'])


# def db_add(db_obj):
#     session.add(db_obj)
#     session.commit()
#
#
# def db_rm(db_obj):
#     session.delete(db_obj)
#     session.commit()


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


# Deprecated. But I would really like to still keep this as a backup solution
# def cookies(test_client_obj):
#     return vars(vars(test_client_obj).get("cookie_jar")).get("_cookies").get("localhost.local").get("/").keys()

