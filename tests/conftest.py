import pytest
from main.app import create_app

from main.data.db_classes.user_db_class import Customer, Employee, Manager


# www.stackoverflow.com/questions/44677426/can-i-pass-arguments-to-pytest-fixtures
@pytest.fixture(scope='module')
def new_user():
    """
    Tests Customer, Employee, and Manager classes
    :return: an object of the
    """
    def _create_user(user_type, title, password, first_name, last_name, email, tel_number, dob, postal_code, address, country):
        if user_type.lower() == 'customer':
            return Customer(first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address)
        elif user_type.lower() == 'employee':
            return Employee(first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address)
        elif user_type.lower() == 'manager':
            return Manager(first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address)
        else:
            raise Exception(f"[TESTING: conftest.py > new_user()] Unknown user type {user_type}")

    return _create_user


# www.patricksoftwareblog.com/testing-a-flask-application-using-pytest
@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()  # NOTE: "Test Configuration" missing

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


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
