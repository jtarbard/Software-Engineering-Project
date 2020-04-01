import datetime
import pprint
import flask
from bs4 import BeautifulSoup

import tests.conftest as conftest


def test_register_get_basic(test_client):
    """
    GIVEN a Flask application
    WHEN the '/account/register' page is requested (GET)
    UNDER CONDITIONS ... TBA
    THEN check the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/register' (OPTIONS, HEAD, GET) -> account.register_get>
    """
    assert False


def test_register_post_basic(test_client):
    """
    GIVEN a Flask application with no cookies
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS ... TBA
    THEN check the response is valid

    TESTING FOR <Rule '/account/register' (OPTIONS, POST) -> account.register_post>
    """
    assert False


# (can use) db_session (as a fixture) from pytest-flask-sqlalchemy to modify the test database.
# but i think mocking & patching is more of my style.
def test_login_get_basic(app, test_client, mocker):
    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. No cookies
    THEN check the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.get('/account/login', follow_redirects=True)
        soup = BeautifulSoup(rv.data, 'html.parser')

        assert "Login" in soup.title.string
        assert rv.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == '/account/login_register.html'

    # ------------------------------------------------------- #

    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. Has basket cookies
                     3. Has random cookies
    THEN check basket cookie is cleared, the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should be removed")
        test_client.set_cookie("localhost", "random_cookie", "this should persist")

        # extremely primitive way to access cookies, because flask.request doesn't work in test context for some reason
        rv = test_client.get('/account/login', follow_redirects=True)
        soup = BeautifulSoup(rv.data, 'html.parser')

        assert rv.status_code == 200
        assert "Login" in soup.title.string
        assert "vertex_basket_cookie" not in conftest.cookies(test_client)
        assert "random_cookie" in conftest.cookies(test_client)
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == '/account/login_register.html'

    # ------------------------------------------------------- #

    # Mocked side effect
    def return_user_response(request, needs_login):
        return True, flask.redirect("/account/login")  # TODO: return a real user instead of True

    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_user_response)

    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. No cookies
    THEN check the page correctly renders (and gives valid response)
         1. Redirect to index page
         2. '/index/index.html' gets rendered

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        # Note: Pretend user is successfully returned
        rv = test_client.get("/account/login", follow_redirects=True)
        soup = BeautifulSoup(rv.data, 'html.parser')

        assert 'Index' in soup.title.string
        assert rv.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == '/index/index.html'

    # db_session.add(new_user('customer'))
    # db_session.commit()

    # ------------------------------------------------------- #

    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. Basket cookies exist
    THEN check the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should persist")
        test_client.set_cookie("localhost", "random_cookie", "this should persist")

        rv = test_client.get("/account/login", follow_redirects=True)
        pprint.pprint(flask.request.cookies)
        soup = BeautifulSoup(rv.data, 'html.parser')

        # Shouldn't clear basket cookies (or any other cookies)
        assert "vertex_basket_cookie" in conftest.cookies(test_client)
        assert "random_cookie" in conftest.cookies(test_client)

        # Redirects to Index
        assert 'Index' in soup.title.string
        assert rv.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == '/index/index.html'


def test_login_get_extra(test_client):
    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. Contains some other cookies
    THEN check the page correctly renders, and those other cookies are retained (and gives valid response)

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    # TODO: Implement
    assert True


def test_login_post_basic(test_client):
    """
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS ... TBA
    THEN check the response is valid

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    assert False


def test_logout_get_basic(test_client):
    """
    GIVEN a Flask application
    WHEN the '/account/log_out' page is requested (GET)
    UNDER CONDITIONS ... TBA
    THEN check the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/log_out' (OPTIONS, HEAD, GET) -> account.log_out>
    """
    assert False
