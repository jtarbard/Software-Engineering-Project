import datetime
import random
import pprint
import copy
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


def test_register_post_basic(app, test_client, mocker, template_checker, new_user):

    def assert_html_renders(exp_fields: dict):
        soup = BeautifulSoup(rv.data, 'html.parser')

        # Check textboxes & dob
        for textbox in soup.find_all("input"):
            for key, value in exp_fields.items():
                if textbox.get("name") == key:
                    assert textbox.get("value") == value

        # Check dropdowns
        for option in soup.find_all('option'):
            if option.get("value") == exp_fields.get("title", "title_is_not_expected") or \
               option.get("value") == exp_fields.get("country", "country_is_not_expected"):
                assert option.get("selected") is not None

    """
    PRELIMINARY DATABASE CONDITIONS:
    + Customer = new_user
    + Employee = new_user
    + Manager = new_user
    """
    from main.data.db_session import database
    from main.data.db_classes.user_db_class import User
    database.session.add(new_user("customer"))
    database.session.add(new_user("employee"))
    database.session.add(new_user("manager"))

    # Valid data:
    valid_title = "Mrs"
    valid_password_first = "passw0rD"
    valid_first_name = "Jane"
    valid_last_name = "Doe"
    valid_email = "janedoe_newi@gmail.com"
    valid_tel_number = "7654896522"
    valid_dob = datetime.date(1999, 1, 1)
    valid_postcode = "LS2 3WE"
    valid_address = "Somewhere over the rainbow"
    valid_country = "GB"
    valid_dict = dict(title=valid_title, password_first=valid_password_first, password_second=valid_password_first,
                      first_name=valid_first_name, last_name=valid_last_name,
                      email=valid_email, tel_number=valid_tel_number, dob=valid_dob,
                      postcode=valid_postcode, address=valid_address, country=valid_country)
    valid_dict_password_cleared = copy.deepcopy(valid_dict)
    # valid_dict_password_cleared["date_of_birth"] = valid_dob
    del valid_dict_password_cleared["password_first"]
    del valid_dict_password_cleared["password_second"]
    valid_dict_password_cleared["dob"] = str(valid_dob)

    invalid_charsets = ["@_!#$%^&*()<>?/", "\\|}{~:filler"]

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_1
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. Email does not exist in database
                     3. Email is of correct format: "email@domain.[com,etc]"
                     4. Password length is 8-15
                     5. Password contains at least a number
                     6. Password and has no invalid characters nor spaces
                     7. First password matches second password
                     8. First name length is 8-15 and has no invalid characters
                     9. Last name length is 8-15 and has no invalid characters
                     10. Tel number is numeric and length is 7-11
                     11. Date of Birth evaluates to user being over 16 years old
                     12. Postcode is "valid" according to UK gov (unfortunately this site isn't very international) and has no invalid characters
                     13. Address length is 10-40 and has no invalid characters
                     14. Country length is 2-5 and has no invalid characters
                     15. Country is in the list of countries
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/home"
               3. page_title or _main_layout title has "Your Account"
               4. "account/account.html" is rendered
               5. vertex_account_cookie is created
               6. User is created in database

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.post('/account/register', data=valid_dict, follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Your Account",
                         exp_url="/account/home", exp_template_path='/account/account.html',
                         exp_exist_cookies=["vertex_account_cookie"])

        assert User.query.filter(User.email == valid_email) is not None

    test_client.delete_cookie("localhost", "vertex_account_cookie")

    # ------------------------------------------------------- #

    valid_dict["email"] = "newvalidemail@gmail.com"
    valid_dict_password_cleared["email"] = "newvalidemail@gmail.com"

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_2
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Email exists in database
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        email_exists_dict = copy.deepcopy(valid_dict)
        email_exists_dict["email"] = "johndoe@thevertex.com"
        exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
        exp_retained_dict["email"] = "johndoe@thevertex.com"

        rv = test_client.post('/account/register', data=email_exists_dict, follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                         exp_url="/account/register", exp_template_path='/account/login_register.html',
                         exp_exist_cookies=[],
                         exp_template_context=exp_retained_dict)

        assert_html_renders(exp_retained_dict)


    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_3
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Email is of wrong format
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_emails = ["johndoe", "johndoe@gmail", "johndoe@gmail."]

    for invalid_email in invalid_emails:
        with conftest.captured_templates(app) as templates:
            email_wrong_format_dict = copy.deepcopy(valid_dict)
            email_wrong_format_dict["email"] = invalid_email
            exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
            exp_retained_dict["email"] = invalid_email

            rv = test_client.post('/account/register', data=email_wrong_format_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=exp_retained_dict)

            assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_4
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Password length is out of 8-15
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_pws = ["", "supermegalongpassw0rD"]

    for invalid_pw in invalid_pws:
        with conftest.captured_templates(app) as templates:
            password_wrong_length_dict = copy.deepcopy(valid_dict)
            password_wrong_length_dict["password_first"] = invalid_pw
            password_wrong_length_dict["password_second"] = invalid_pw

            rv = test_client.post('/account/register', data=password_wrong_length_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=valid_dict_password_cleared)

            assert_html_renders(valid_dict_password_cleared)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_5
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Password does not have a number
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_pws = ["password", "nonumberyay"]

    for invalid_pw in invalid_pws:
        with conftest.captured_templates(app) as templates:
            password_wrong_length_dict = copy.deepcopy(valid_dict)
            password_wrong_length_dict["password_first"] = invalid_pw
            password_wrong_length_dict["password_second"] = invalid_pw

            rv = test_client.post('/account/register', data=password_wrong_length_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=valid_dict_password_cleared)

            assert_html_renders(valid_dict_password_cleared)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_6
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Password has invalid characters, OR spaces
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_pws = invalid_charsets + ["I have space"]

    for invalid_pw in invalid_pws:
        with conftest.captured_templates(app) as templates:
            password_wrong_length_dict = copy.deepcopy(valid_dict)
            password_wrong_length_dict["password_first"] = invalid_pw
            password_wrong_length_dict["password_second"] = invalid_pw

            rv = test_client.post('/account/register', data=password_wrong_length_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=valid_dict_password_cleared)

            assert_html_renders(valid_dict_password_cleared)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_7
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. First and second passwords don't match
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """

    with conftest.captured_templates(app) as templates:
        password_wrong_length_dict = copy.deepcopy(valid_dict)
        password_wrong_length_dict["password_first"] = "validPW0"
        password_wrong_length_dict["password_second"] = "unmatchPW0"

        rv = test_client.post('/account/register', data=password_wrong_length_dict, follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                         exp_url="/account/register", exp_template_path='/account/login_register.html',
                         exp_exist_cookies=[],
                         exp_template_context=valid_dict_password_cleared)

        assert_html_renders(valid_dict_password_cleared)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_8
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. First name length is out of 3-15, OR has invalid characters
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_first_names = invalid_charsets + ["", "12345678", "supermegalongbutstillvalidnames"]

    for invalid_first_name in invalid_first_names:
        with conftest.captured_templates(app) as templates:
            invalid_first_name_dict = copy.deepcopy(valid_dict)
            invalid_first_name_dict["first_name"] = invalid_first_name
            exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
            exp_retained_dict["first_name"] = invalid_first_name

            rv = test_client.post('/account/register', data=invalid_first_name_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=exp_retained_dict)

            assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_9
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Last name length is out of 3-15, OR has invalid characters
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_last_names = invalid_charsets + ["", "12345678", "supermegalongbutstillvalidnames"]

    for invalid_last_name in invalid_last_names:
        with conftest.captured_templates(app) as templates:
            invalid_first_name_dict = copy.deepcopy(valid_dict)
            invalid_first_name_dict["last_name"] = invalid_last_name
            exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
            exp_retained_dict["last_name"] = invalid_last_name

            rv = test_client.post('/account/register', data=invalid_first_name_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=exp_retained_dict)

            assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_10
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Tel number is NOT numeric, OR length out of 7-11
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_tels = invalid_charsets + ["", "1234567891234567891234567890", "notnumeric", "1234567a"]

    for invalid_tel in invalid_tels:
        with conftest.captured_templates(app) as templates:
            invalid_first_name_dict = copy.deepcopy(valid_dict)
            invalid_first_name_dict["tel_number"] = invalid_tel
            exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
            exp_retained_dict["tel_number"] = invalid_tel

            rv = test_client.post('/account/register', data=invalid_first_name_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=exp_retained_dict)

            assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_11
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Date of Birth evaluates user to be less than 16 years old, OR in the future
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_dobs = [datetime.date.today()-datetime.timedelta(days=365*16+3),
                    datetime.date.today(),
                    datetime.date.today()+datetime.timedelta(days=365*20)]

    for invalid_dob in invalid_dobs:
        with conftest.captured_templates(app) as templates:
            invalid_first_name_dict = copy.deepcopy(valid_dict)
            invalid_first_name_dict["dob"] = invalid_dob
            exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
            exp_retained_dict["dob"] = str(invalid_dob)

            rv = test_client.post('/account/register', data=invalid_first_name_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=exp_retained_dict)

            assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_11b
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Date of Birth is of invalid date
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    # invalid_dobs = ["2000-1-32",
    #                 "1999-2-29",
    #                 "2000-4-31",
    #                 "2000-6-31",
    #                 "2000-9-31",
    #                 "2000-11-31"]
    #
    # for invalid_dob in invalid_dobs:
    #     with conftest.captured_templates(app) as templates:
    #         invalid_first_name_dict = copy.deepcopy(valid_dict)
    #         invalid_first_name_dict["dob"] = invalid_dob
    #         exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
    #         exp_retained_dict["dob"] = str(invalid_dob)
    #
    #         rv = test_client.post('/account/register', data=invalid_first_name_dict, follow_redirects=True)
    #
    #         template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
    #                          exp_url="/account/register", exp_template_path='/account/login_register.html',
    #                          exp_exist_cookies=[],
    #                          exp_template_context=exp_retained_dict)
    #
    #         assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_12
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Postcode is "invalid"
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_postcodes = ["999078", "ABCDEFG123"]

    for invalid_postcode in invalid_postcodes:
        with conftest.captured_templates(app) as templates:
            invalid_first_name_dict = copy.deepcopy(valid_dict)
            invalid_first_name_dict["postcode"] = invalid_postcode
            exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
            exp_retained_dict["postcode"] = invalid_postcode

            rv = test_client.post('/account/register', data=invalid_first_name_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=exp_retained_dict)

            assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_13
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Address length is out of 10-40, OR has invalid characters
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_addresses = invalid_charsets + ["", "long"*15]

    for invalid_address in invalid_addresses:
        with conftest.captured_templates(app) as templates:
            invalid_first_name_dict = copy.deepcopy(valid_dict)
            invalid_first_name_dict["address"] = invalid_address
            exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
            exp_retained_dict["address"] = invalid_address

            rv = test_client.post('/account/register', data=invalid_first_name_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=exp_retained_dict)

            assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    """
    Register_Post_Basic_Test_14
    GIVEN a Flask application
    WHEN data form is submitted to the '/account/register' page (POST)
    UNDER CONDITIONS 1. 3 users exist in database
                     2. All valid, except:
                     3. Country length is out of 2-5, OR has invalid characters (naturally, not in list)
    THEN check 1. Valid status code (200)
               2. Redirected url is "/account/register"
               3. page_title or _main_layout title has "Register"
               4. "account/login_register.html" is rendered
               5. No cookies exist
               6. All data except passwords are retained (or rather, the passwords are cleared)
               7. Check the raw HTML that all fields are actually used

    TESTING FOR <Rule '/account/login' (OPTIONS, POST) -> account.login_post>
    """
    invalid_countries = ["@_!#", "$%^&", "*()<", ">?/\\", "|}", ":{~", "", "longgggg"]

    for invalid_country in invalid_countries:
        with conftest.captured_templates(app) as templates:
            invalid_first_name_dict = copy.deepcopy(valid_dict)
            invalid_first_name_dict["country"] = invalid_country
            exp_retained_dict = copy.deepcopy(valid_dict_password_cleared)
            exp_retained_dict["country"] = invalid_country

            rv = test_client.post('/account/register', data=invalid_first_name_dict, follow_redirects=True)

            template_checker(response=rv, request=flask.request, templates=templates, exp_title="Register",
                             exp_url="/account/register", exp_template_path='/account/login_register.html',
                             exp_exist_cookies=[],
                             exp_template_context=exp_retained_dict)

            assert_html_renders(exp_retained_dict)

    # ------------------------------------------------------- #

    database.session.rollback()  # Cleaning test database.

    # --------------------------------- END OF THIS TEST: test_register_post_basic --------------------------------- #


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


def test_login_post_basic(app, test_client, new_user, template_checker):
    """
    PRELIMINARY DATABASE CONDITIONS:
    + Customer = new_user
    + Employee = new_user
    + Manager = new_user
    """
    from main.data.db_session import database
    database.session.add(new_user("customer"))
    database.session.add(new_user("employee"))
    database.session.add(new_user("manager"))

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

    database.session.rollback()  # Cleaning test database.

    # --------------------------------- END OF THIS TEST: test_login_post_basic --------------------------------- #


# def test_login_post_extra():
#     # User is logged in. This should have been covered in login_get though. (i.e. Post method cannot be called - no data form can be submitted because Get method already redirected to another page)
#     # Empty email. maybe can test in basic?
#     # Weird email format - e.g. no @domain.[com]
#     # Unicode in data form
#     # SQL Injection :)


def test_logout_get_basic(app, test_client, template_checker):
    """
    Logout_Get_Basic_Test_1
    GIVEN a Flask application
    WHEN the '/account/log_out' page is requested (GET)
    UNDER CONDITIONS 1. User logged in (i.e. vertex_account_cookie exists)
                     2. No other cookies exist
    THEN check 1. Valid status code (200)
               2. The redirected url is "/" (index)
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. vertex_account_cookie is deleted (i.e. user is logged out)

    TESTING FOR <Rule '/account/log_out' (OPTIONS, HEAD, GET) -> account.log_out>
    """

    with conftest.captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_account_cookie", "this should be deleted")

        rv = test_client.get("/account/log_out", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=[])

    # ------------------------------------------------------- #

    """
    Logout_Get_Basic_Test_2
    GIVEN a Flask application
    WHEN the '/account/log_out' page is requested (GET)
    UNDER CONDITIONS 1. User logged in (i.e. vertex_account_cookie exists)
                     2. Basket cookies exist
    THEN check 1. Valid status code (200)
               2. The redirected url is "/" (index)
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. vertex_account_cookie is deleted (i.e. user is logged out)
               6. vertex_basket_cookie is deleted

    TESTING FOR <Rule '/account/log_out' (OPTIONS, HEAD, GET) -> account.log_out>
    """

    with conftest.captured_templates(app) as templates:
        test_client.set_cookie("localhost", "vertex_account_cookie", "this should be deleted")
        test_client.set_cookie("localhost", "vertex_basket_cookie", "this should be deleted")

        rv = test_client.get("/account/log_out", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=[])

    # --------------------------------- END OF THIS TEST: test_logout_get_basic --------------------------------- #


def test_logout_get_extra(app, test_client, template_checker):
    """
    Logout_Get_Extra_Test_1
    GIVEN a Flask application
    WHEN the '/account/log_out' page is requested (GET)
    UNDER CONDITIONS 1. User NOT logged in (i.e. vertex_account_cookie DOES NOT exist)
                     2. No other cookies exist
    THEN check 1. Valid status code (200)
               2. The redirected url is "/" (index)
               3. page_title (rendered template parameter) or actual page title has "Index"
               4. '/index/index.html' is rendered
               5. vertex_account_cookie is deleted (i.e. user is logged out)

    TESTING FOR <Rule '/account/log_out' (OPTIONS, HEAD, GET) -> account.log_out>
    """

    with conftest.captured_templates(app) as templates:
        rv = test_client.get("/account/log_out", follow_redirects=True)

        template_checker(response=rv, request=flask.request, templates=templates, exp_title="Index",
                         exp_url="/", exp_template_path='/index/index.html',
                         exp_exist_cookies=[])

    # --------------------------------- END OF THIS TEST: test_logout_get_extra --------------------------------- #