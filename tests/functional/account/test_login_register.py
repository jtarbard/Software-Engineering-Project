import flask
from bs4 import BeautifulSoup


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


def test_login_get_basic(test_client):
    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. No cookies
    THEN check the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """
    response = test_client.get("/account/login")
    soup = BeautifulSoup(response.data, 'html.parser')

    assert response.status_code == 200
    assert "Login" in soup.title.string

    # ------------------------------------------------------- #

    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. Has basket cookies
    THEN check basket cookie is cleared, the page correctly renders (and gives valid response)
    
    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """
    test_client.set_cookie("vertex_basket_cookie", "something")
    response = test_client.get("/account/login")
    soup = BeautifulSoup(response.data, 'html.parser')

    assert response.status_code == 200
    assert "Login" in soup.title.string
    assert flask.request.cookies.get("vertex_basket_cookie", None) is None

    # ------------------------------------------------------- #

    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. No cookies
    THEN check the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """
    # TODO: Involves database. Is this still "unit-ly functional"? Also how
    # TODO: Maybe decouple client (app) creation and database creation? So only use part of configure()

    assert False

    # ------------------------------------------------------- #

    """
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. Basket cookies exist
    THEN check the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """
    # TODO: Implement. Involves database

    assert False


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
    assert False


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
