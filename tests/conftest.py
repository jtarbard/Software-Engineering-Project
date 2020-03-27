import pytest
import os
import re
from main.app import create_app

from main.data.db_classes.user_db_class import Customer, Employee, Manager


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
    def _create_user(user_type, **kwargs):
        if user_type.lower() == 'customer':
            return Customer(**kwargs)
        elif user_type.lower() == 'employee':
            return Employee(**kwargs)
        elif user_type.lower() == 'manager':
            return Manager(**kwargs)
        else:
            raise Exception(f"[TESTING: conftest.py > new_user()] Unknown user type {user_type}")

    return _create_user


import tempfile
# www.patricksoftwareblog.com/testing-a-flask-application-using-pytest
@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()  # NOTE: "Test Configuration" missing
    # db_fd, flask_app.config['DATABASE'] = tempfile.mkstemp()
    # flask_app.config['TESTING'] = True

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()
    # os.close(db_fd)
    # os.unlink(flask_app.config['DATABASE'])


@pytest.fixture(scope='class')
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


# www.patricksoftwareblog.com/testing-a-flask-application-using-pytest
# @pytest.fixture(scope='module')
# def init_database():
#     # Create the database and the database table
#     db.create_all()
#
#     # Insert user data
#     user1 = User(email='patkennedy79@gmail.com', plaintext_password='FlaskIsAwesome')
#     user2 = User(email='kennedyfamilyrecipes@gmail.com', plaintext_password='PaSsWoRd')
#     db.session.add(user1)
#     db.session.add(user2)
#
#     # Commit the changes for the users
#     db.session.commit()
#
#     yield db  # this is where the testing happens!
#
#     db.drop_all()
