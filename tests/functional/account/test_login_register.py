import datetime
import random
import string
import pprint
import flask
from bs4 import BeautifulSoup

import tests.conftest as conftest


def test_register_get_basic(app, test_client, mocker, template_checker):

    # Mocked side effect
    def return_logged_in_user_response(request, needs_login):
        return True, flask.redirect("/account/login")  # TODO: return a real user instead of True

    def return_not_logged_in_user_response(request, needs_login):
        return False, flask.redirect("/account/login")

    # ------------------------------------------------------- #

    # Pretend user not logged in
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_not_logged_in_user_response)

    # ------------------------------------------------------- #

    """
    Register_Get_Basic_Test_1
    GIVEN a Flask application
    WHEN the '/account/register' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. No cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/account/register"
               3. page_title (rendered template parameter) or actual page title has "Register"
               4. '/account/login_register.html' is rendered
               5. No cookies are created

    TESTING FOR <Rule '/account/register' (OPTIONS, HEAD, GET) -> account.register_get>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.get('/account/register', follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                         exp_url="/account/register", exp_template_path='/account/login_register.html',
                         exp_exist_cookies=[])

    # ------------------------------------------------------- #

    """
    Login_Get_Basic_Test_2
    GIVEN a Flask application
    WHEN the '/account/register' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. Has basket cookies
                     3. Has random cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/account/register"
               3. page_title (rendered template parameter) or actual page title has "Register"
               4. '/account/login_register.html' is rendered
               5. Basket cookie is deleted
               6. Other random cookies are retained

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should be removed")
        test_client.set_cookie("localhost", "random_cookie7", "this should persist")
        test_client.set_cookie("localhost", "random_cookie11", "this should persist")

        # extremely primitive way to access cookies, because flask.request doesn't work in test context for some reason
        rv = test_client.get('/account/register', follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                         exp_url="/account/register", exp_template_path='/account/login_register.html',
                         exp_exist_cookies=["random_cookie7", "random_cookie11"],
                         exp_non_exist_cookies=["vertex_basket_cookie"])

    # remove cookies so test_client is clean again
    test_client.delete_cookie("localhost", "random_cookie7")
    test_client.delete_cookie("localhost", "random_cookie11")

    # ------------------------------------------------------- #

    # Note: Pretend user is successfully returned
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_logged_in_user_response)

    # ------------------------------------------------------- #

    """
    Login_Get_Basic_Test_3
    GIVEN a Flask application
    WHEN the '/account/register' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. No cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/" (homepage)
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. No cookies are created

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.get("/account/register", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=[])

    # ------------------------------------------------------- #

    """
    Login_Get_Basic_Test_4
    GIVEN a Flask application
    WHEN the '/account/register' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. Basket cookies exist
                     3. Has random cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/" (homepage)
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. All cookies are retained

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should persist")
        test_client.set_cookie("localhost", "random_cookie13", "this should persist")
        test_client.set_cookie("localhost", "random_cookie17", "this should persist")

        rv = test_client.get("/account/register", follow_redirects=True)

        # Shouldn't clear basket cookies (or any other cookies)
        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=["vertex_basket_cookie", "random_cookie13", "random_cookie17"])

    # --------------------------------- END OF THIS TEST: test_register_get_basic --------------------------------- #


def test_register_post_basic(test_client):
    """
    GIVEN a Flask application with no cookies
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS ... TBA
    THEN check the response is valid

    TESTING FOR <Rule '/account/register' (OPTIONS, POST) -> account.register_post>
    """
    assert False


def test_login_get_basic(app, test_client, mocker, template_checker):

    # Mocked side effect
    def return_logged_in_user_response(request, needs_login):
        return True, flask.redirect("/account/login")  # TODO: return a real user instead of True

    def return_not_logged_in_user_response(request, needs_login):
        return False, flask.redirect("/account/login")

    # ------------------------------------------------------- #

    """
    Login_Get_Basic_Test_1
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. No cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/account/login"
               3. page_title (rendered template parameter) or actual page title has "Login"
               4. '/account/login_register.html' is rendered
               5. No cookies are created

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_not_logged_in_user_response)

    with conftest.captured_templates(app) as templates:
        rv = test_client.get('/account/login', follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_exist_cookies=[])

    # ------------------------------------------------------- #

    """
    Login_Get_Basic_Test_2
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. Has basket cookies
                     3. Has random cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/account/login"
               3. page_title (rendered template parameter) or actual page title has "Login"
               4. '/account/login_register.html' is rendered
               5. Basket cookie is deleted
               6. Other random cookies are retained

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should be removed")
        test_client.set_cookie("localhost", "random_cookie7", "this should persist")
        test_client.set_cookie("localhost", "random_cookie11", "this should persist")

        # extremely primitive way to access cookies, because flask.request doesn't work in test context for some reason
        rv = test_client.get('/account/login', follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_exist_cookies=["random_cookie7", "random_cookie11"],
                         exp_non_exist_cookies=["vertex_basket_cookie"])

    # remove cookies so test_client is clean again
    test_client.delete_cookie("localhost", "random_cookie7")
    test_client.delete_cookie("localhost", "random_cookie11")

    # ------------------------------------------------------- #

    # Note: Pretend user is successfully returned
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_logged_in_user_response)

    """
    Login_Get_Basic_Test_3
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. No cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/" (homepage)
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. No cookies are created

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.get("/account/login", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=[])

    # ------------------------------------------------------- #

    """
    Login_Get_Basic_Test_4
    GIVEN a Flask application
    WHEN the '/account/login' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. Basket cookies exist
                     3. Has random cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/" (homepage)
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. All cookies are retained

    TESTING FOR <Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
    """

    with conftest.captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should persist")
        test_client.set_cookie("localhost", "random_cookie13", "this should persist")
        test_client.set_cookie("localhost", "random_cookie17", "this should persist")

        rv = test_client.get("/account/login", follow_redirects=True)

        # Shouldn't clear basket cookies (or any other cookies)
        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=["vertex_basket_cookie", "random_cookie13", "random_cookie17"])

    # --------------------------------- END OF THIS TEST: test_login_get_basic --------------------------------- #


def test_login_post_basic(app, test_client, mocker, new_user, template_checker):

    """
    PRELIMINARY DATABASE CONDITIONS:
    + Customer = new_user
    + Employee = new_user
    + Manager = new_user
    """
    from main.data.db_session import add_to_database, delete_from_database
    add_to_database(new_user("customer"))
    add_to_database(new_user("employee"))
    add_to_database(new_user("manager"))

    # ------------------------------------------------------- #

    """
    Login_Post_Basic_Test_1
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS 1. user exists in database
                     2. existent email
                     3. existent password
                     4. Password length is 8-15 and has no invalid characters
                     5. email and password are matching
    THEN check 1. Valid status code (200)
               2. Redirected route is "account.view_account" (the function called is view_account())
               3. page_title or _main_layout title has "Your Account"
               4. "account/account.html" is rendered
               5. vertex_account_cookie is created

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/login', data=dict(email="johndoe@thevertex.com",
                                                          password="passw0rD"), follow_redirects=True)
        soup = BeautifulSoup(rv.data, 'html.parser')

        exp_title = "Your Account"

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Your Account",
                         exp_url=flask.url_for("account.view_account"), exp_template_path='/account/account.html',
                         exp_exist_cookies=["vertex_account_cookie"])

    test_client.delete_cookie("localhost", "vertex_account_cookie")

    # ------------------------------------------------------- #

    """
    Login_Post_Basic_Test_2
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS 1. user exists in database
                     2. existent email
                     3. existent password
                     4. Password length is 8-15 and has no invalid characters
                     5. email and password are NOT matching
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/login"
               3. page_title or _main_layout title has "Login"
               4. "account/login_register.html" is rendered
               5. Email is retained
               6. ServerError should describe email and password are NOT matching (Currently, "Input error: Incorrect email or password")

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/login', data=dict(email="johndoe@thevertex.com",
                                                          password="Admin666"), follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_template_context={"email": "johndoe@thevertex.com",
                                               "ServerError": "Input error: Incorrect email or password"})

    # ------------------------------------------------------- #

    """
    Login_Post_Basic_Test_3
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS 1. when user exists in database
                     2. existent email
                     3. NON-EXISTENT password
                     4. Password length is 8-15 and has no invalid characters
                     5. email and password are NOT matching
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/login"
               3. page_title or _main_layout title has "Login"
               4. "account/login_register.html" is rendered
               5. Email is retained
               6. ServerError should describe email and password are NOT matching (Currently, "Input error: Incorrect email or password")

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/login', data=dict(email="johndoe@thevertex.com",
                                                          password="Admin667"), follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_template_context={"email": "johndoe@thevertex.com",
                                               "ServerError": "Input error: Incorrect email or password"})

    # ------------------------------------------------------- #

    """
    Login_Post_Basic_Test_4
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS 1. when user exists in database
                     2. NON-EXISTENT email
                     3. existent password
                     4. Password length is 8-15 and has no invalid characters
                     5. email and password are NOT matching
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/login"
               3. page_title or _main_layout title has "Login"
               4. "account/login_register.html" is rendered
               5. Email is retained
               6. ServerError should describe email is not found (Currently, "Input error: Incorrect email or password")

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/login', data=dict(email="doesnotexist@vertex.com",
                                                          password="Admin666"), follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_template_context={"email": "doesnotexist@vertex.com",
                                               "ServerError": "Input error: Incorrect email or password"})

    # ------------------------------------------------------- #

    """
    Login_Post_Basic_Test_5
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS 1. when user exists in database
                     2. NON-EXISTENT email
                     3. NON-EXISTENT password
                     4. Password length is 8-15 and has no invalid characters
                     5. email and password are NOT matching
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/login"
               3. page_title or _main_layout title has "Login"
               4. "account/login_register.html" is rendered
               5. Email is retained
               6. ServerError should describe email is not found (Currently, "Input error: Incorrect email or password")

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/login', data=dict(email="doesnotexist@vertex.com",
                                                          password="Admin667"), follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_template_context={"email": "doesnotexist@vertex.com",
                                               "ServerError": "Input error: Incorrect email or password"})

    # ------------------------------------------------------- #

    """
    Login_Post_Basic_Test_6
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS 1. when user exists in database
                     2. Existent email
                     3. NON-EXISTENT password
                     4. Password length OUT OF 8-15 range
                     5. Password has no invalid characters
                     6. email and password are (naturally) NOT matching
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/login"
               3. page_title or _main_layout title has "Login"
               4. "account/login_register.html" is rendered
               5. Email is retained
               6. ServerError should describe password is of wrong size (Currently, "Input error: password is not of correct size (8-15)")

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/login', data=dict(email="johndoe@thevertex.com",
                                                          password=""), follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_template_context={"email": "johndoe@thevertex.com",
                                               "ServerError": "Input error: password is not of correct size (8-15)"})

    # ------------------------------------------------------- #

    """
    Login_Post_Basic_Test_7
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS 1. when user exists in database
                     2. Existent email
                     3. NON-EXISTENT password
                     4. Password length is 8-15
                     5. Password HAS INVALID characters
                     6. email and password are (naturally) NOT matching
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/login"
               3. page_title or _main_layout title has "Login"
               4. "account/login_register.html" is rendered
               5. Email is retained
               6. ServerError should describe password contains invalid characters (Currently, "Input Error: Password not in valid format")

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/login', data=dict(email="johndoe@thevertex.com",
                                                          password="password@"), follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_template_context={"email": "johndoe@thevertex.com",
                                               "ServerError": "Input Error: Password not in valid format"})

    # ------------------------------------------------------- #

    """
    Login_Post_Basic_Test_8
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/login' page (POST)
    UNDER CONDITIONS 1. when user exists in database
                     2. Existent email
                     3. NON-EXISTENT password
                     4. Password length is OUT OF 8-15 range
                     5. Password HAS INVALID characters
                     6. email and password are (naturally) NOT matching
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/login"
               3. page_title or _main_layout title has "Login"
               4. "account/login_register.html" is rendered
               5. Email is retained
               6. ServerError should describe either: password is of wrong size (Currently, "Input error: password is not of correct size (8-15)"), or
                                                      password contains invalid characters (Currently, "Input Error: Password not in valid format")

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/login', data=dict(email="johndoe@thevertex.com",
                                                          password="password@"), follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Login",
                         exp_url="/account/login", exp_template_path='/account/login_register.html',
                         exp_template_context={"email": "johndoe@thevertex.com",
                                               "ServerError": ["Input error: password is not of correct size (8-15)", "Input Error: Password not in valid format"]})

    # TODO: Potentially add 3 more tests: Non-Existent email, invalid password format -> should throw error says invalid password "without connecting to database".

    # ------------------------------------------------------- #

    # Cleaning test database. TODO: Perhaps can use SAVEPOINT and rollback?
    delete_from_database(new_user("customer"))
    delete_from_database(new_user("employee"))
    delete_from_database(new_user("manager"))

    # --------------------------------- END OF THIS TEST: test_login_post_basic --------------------------------- #


# def test_login_post_extra():
#     # Empty email. maybe can test in basic?
#     # Weird email format - e.g. no @domain.[com]
#     # Unicode in data form
#     # SQL Injection :)


def test_logout_get_basic(test_client):
    """
    GIVEN a Flask application
    WHEN the '/account/log_out' page is requested (GET)
    UNDER CONDITIONS ... TBA
    THEN check the page correctly renders (and gives valid response)

    TESTING FOR <Rule '/account/log_out' (OPTIONS, HEAD, GET) -> account.log_out>
    """
    assert False
