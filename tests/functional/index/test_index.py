import flask

from main.helper_functions.test_helpers.flask_signal_capturer import captured_templates
from main.helper_functions.test_helpers.mocked_functions import return_logged_in_user_response, return_not_logged_in_user_response


def test_index_func_basic(app, test_client, mocker, template_checker):

    # ------------------------------------------------------- #

    # Pretend user not logged in
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_not_logged_in_user_response)

    # ------------------------------------------------------- #

    """
    Index_Func_Basic_Test_1
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. No cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/"
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. No cookies are created

    TESTING FOR <Rule '/' (OPTIONS, HEAD, GET) -> index.index_func>
    """

    with captured_templates(app) as templates:
        rv = test_client.get("/", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=[])

    # ------------------------------------------------------- #

    """
    Index_Func_Basic_Test_2
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. Has basket cookies
                     3. Has random cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/"
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. All cookies are retained

    TESTING FOR <Rule '/' (OPTIONS, HEAD, GET) -> index.index_func>
    """

    with captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should persist")
        test_client.set_cookie("localhost", "random_cookie23", "this should persist")
        test_client.set_cookie("localhost", "random_cookie29", "this should persist")

        # extremely primitive way to access cookies, because flask.request doesn't work in test context for some reason
        rv = test_client.get("/", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=["vertex_basket_cookie", "random_cookie23", "random_cookie29"])

    # ------------------------------------------------------- #

    # remove cookies so test_client is clean again
    test_client.delete_cookie("localhost", "vertex_basket_cookie")
    test_client.delete_cookie("localhost", "random_cookie23")
    test_client.delete_cookie("localhost", "random_cookie29")

    # ------------------------------------------------------- #

    # Note: Pretend user is successfully returned
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_logged_in_user_response)

    # ------------------------------------------------------- #

    """
    Index_Func_Basic_Test_3
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    UNDER CONDITIONS 1. User logged in
                     2. No cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/"
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. No cookies are created

    TESTING FOR <Rule '/' (OPTIONS, HEAD, GET) -> index.index_func>
    """

    with captured_templates(app) as templates:
        rv = test_client.get("/", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=[])

    # ------------------------------------------------------- #

    """
    Index_Func_Basic_Test_4
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    UNDER CONDITIONS 1. User not logged in
                     2. Has basket cookies
                     3. Has random cookies
    THEN check 1. Valid status code (200)
               2. The redirected url is "/"
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. All cookies are retained

    TESTING FOR <Rule '/' (OPTIONS, HEAD, GET) -> index.index_func>
    """

    with captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should persist")
        test_client.set_cookie("localhost", "random_cookie31", "this should persist")
        test_client.set_cookie("localhost", "random_cookie37", "this should persist")

        rv = test_client.get("/", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=["vertex_basket_cookie", "random_cookie31", "random_cookie37"])

    # --------------------------------- END OF THIS TEST: test_index_func_basic --------------------------------- #
