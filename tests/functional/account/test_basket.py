import flask

from tests.helper.flask_signal_capturer import captured_templates
from tests.helper.mocked_functions import return_logged_in_user_response, return_not_logged_in_user_response


"""
<Rule '/account/basket' (OPTIONS, POST) -> basket.basket_delete_activity>
<Rule '/misc/add_booking_to_basket' (OPTIONS, POST) -> basket.view_classes_post>
"""

def test_basket_view_basic(app, test_client, mocker, template_checker):

    # ------------------------------------------------------- #

    # Pretend user not logged in
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_not_logged_in_user_response)

    # ------------------------------------------------------- #

    """
    Basket_View_Basic_Test_1
    GIVEN a Flask application
    WHEN the '/account/basket' page is requested (GET)
    UNDER CONDITIONS 1. User is logged in (vertex_account_cookie exists)
                     2. cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/account/register"
               3. page_title (rendered template parameter) or actual page title has "Register"
               4. '/account/login_register.html' is rendered
               5. No cookies are created

    TESTING FOR <Rule '/account/basket' (OPTIONS, HEAD, GET) -> basket.basket_view>
    """

    with captured_templates(app) as templates:
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

    with captured_templates(app) as templates:
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

    with captured_templates(app) as templates:
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

    with captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should persist")
        test_client.set_cookie("localhost", "random_cookie13", "this should persist")
        test_client.set_cookie("localhost", "random_cookie17", "this should persist")

        rv = test_client.get("/account/register", follow_redirects=True)

        # Shouldn't clear basket cookies (or any other cookies)
        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=["vertex_basket_cookie", "random_cookie13", "random_cookie17"])

    # --------------------------------- END OF THIS TEST: test_register_get_basic --------------------------------- #


def test_basket_delete_activity_basic():
    assert False


def test_view_classes_post_basic():
    assert False
