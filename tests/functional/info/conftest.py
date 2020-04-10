import pytest


def pytest_generate_tests(metafunc):
    if "membership_view_data" in metafunc.fixturenames:
        metafunc.parametrize("membership_view_data", range(5), indirect=True,
                             ids=["[Basic] Not logged in, No membership",
                                  "[Basic] Logged in, No membership",
                                  "[Basic] Logged in, standard membership",
                                  "[Basic] Logged in, premium membership",
                                  "[Extra] Basket cookie is retained and unmodified"])
    if "buy_membership_data" in metafunc.fixturenames:
        metafunc.parametrize("buy_membership_data", range(10), indirect=True,
                             ids=["[Basic] No basket, add membership. Cooke should be created",
                                  "[Basic] A:1 basket, add membership",
                                  "[Basic] M:1:1 basket, change duration of membership",
                                  "[Basic] M:1:1 basket, upgrade basket membership",
                                  "[Basic] M:2:6 basket, downgrade basket membership",
                                  "[Basic] M:1:6 basket, add invalid membership (Invalid)",
                                  "[Basic] M:1:1 basket. Add membership with duration 0 (Invalid)",
                                  "[Basic] M:1:1 basket. Add membership with negative duration (Invalid)",
                                  "[Extra] Has invalid basket cookie, tries to add more (Invalid)",
                                  "[Extra] A:1 basket. User not logged in, tries to add <Activity 2> to basket (Invalid)"])


@pytest.fixture
def membership_view_data(request):
    """
    Membership_View_Test
    GIVEN a Flask application
    WHEN the '/info/memberships' page is requested (GET)
    VARYING CONDITIONS 1. User with/without membership is logged in / not logged in
    THEN check 1. Valid status code (200)
               2. The redirected url
               3. page_title (rendered template parameter) or actual page title
               4. name of the rendered template
               5. Existing cookies
               6. Standard price is correctly returned
               7. Premium price is correctly returned
               8. Standard membership id is correctly returned
               9. Standard membership id is correctly returned

    TESTING FOR <Rule '/info/memberships' (OPTIONS, HEAD, GET) -> info.membership_view>
    """

    from main.helper_functions.test_helpers.database_creation import activity_objs, activity_type_objs, \
        membership_type_objs
    from main.helper_functions.test_helpers.mocked_functions import return_customer_no_membership_with_no_response, \
        return_customer_premium_with_no_response, \
        return_customer_standard_with_no_response, \
        return_not_logged_in_user_response

    # TODO: Consider refactoring the data in another function so that "data" doesn't need to be re-run n times.
    #       Have 2 functions as "Data Container" and "Data Retrieval"

    # -----------------------------------------| ============= |----------------------------------------- #
    # -----------------------------------------|  Basic Tests  |----------------------------------------- #
    # -----------------------------------------| ============= |----------------------------------------- #

    # Test 0
    # Not logged in, No membership
    # ------
    # 1. vertex_account_cookie does NOT exist
    # 2. User does not have a membership
    if request.param == 0:
        return {"mocked_return_user_response": return_not_logged_in_user_response,
                "create_basket_cookie_and_value": (False, ""),
                "create_account_cookie_and_value": (False, ""),

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": []}

    # Test 1
    # Logged in, No membership
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    elif request.param == 1:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (False, ""),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["vertex_account_cookie"]}

    # Test 2
    # Logged in, standard membership
    # ------
    # 1. vertex_account_cookie exists
    # 2. User has standard membership
    elif request.param == 2:
        return {"mocked_return_user_response": return_customer_standard_with_no_response,
                "create_basket_cookie_and_value": (False, ""),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["vertex_account_cookie"]}

    # Test 3
    # Logged in, premium membership
    # ------
    # 1. vertex_account_cookie exists
    # 2. User has premium membership
    elif request.param == 3:
        return {"mocked_return_user_response": return_customer_premium_with_no_response,
                "create_basket_cookie_and_value": (False, ""),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["vertex_account_cookie"]}

    # -----------------------------------------/ ============= \----------------------------------------- #
    # ----------------------------------------| - Extra Tests - |---------------------------------------- #
    # -----------------------------------------\ ============= /----------------------------------------- #

    # Test 4
    # Basket cookie is retained and unmodified
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. Basket cookie exists
    elif request.param == 4:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"],
                "exp_cookie_values": {"vertex_basket_cookie": "A:1;M:1:1"}}

    else:
        return False


@pytest.fixture
def buy_membership_data(request):
    """
    Buy_Membership_Test
    GIVEN a Flask application
    WHEN new MEMBERSHIP add-to-basket request is submitted to '/info/memberships/buy' route (POST)
    VARYING CONDITIONS 1. User with/without membership is logged in / not logged in (vertex_account_cookie exists or not)
                       2. Basket cookie with ? valid activity
                       3. Basket cookie with ? membership
                       4. The new membership desired & the duration
    THEN check 1. Valid status code (200)
               2. The redirected url
               3. page_title (rendered template parameter) or actual page title
               4. name of the rendered template
               5. Existing cookies
               6. Flashes success / error message
               7. Whether new cookie has new membership correctly appended

    TESTING FOR <Rule '/info/memberships/buy' (OPTIONS, POST) -> info.buy_membership>
    """

    from main.helper_functions.test_helpers.database_creation import activity_objs, activity_type_objs, \
        membership_type_objs
    from main.helper_functions.test_helpers.mocked_functions import return_customer_no_membership_with_no_response, \
        return_customer_premium_with_no_response, \
        return_customer_standard_with_no_response, \
        return_not_logged_in_user_response

    # -----------------------------------------| ============= |----------------------------------------- #
    # -----------------------------------------|  Basic Tests  |----------------------------------------- #
    # -----------------------------------------| ============= |----------------------------------------- #

    # Test 0
    # No basket, add membership. Cooke should be created
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie DOES NOT exist
    if request.param == 0:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (False, ""),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 1,  # membership id. Buying standard (id=1) here
                "membership_duration": 1,  # 1 month

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_basket_cookie", "vertex_account_cookie"],
                "exp_cookie_values": {"vertex_basket_cookie": "M:1:1"},

                "exp_flash_category": "success",
                "exp_flash_message": "Standard Membership has been added to your basket."}

    # Test 1
    # A:1 basket, add membership
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains 1 valid activity (type = 1)
    # 5. Basket cookie has NO membership
    if request.param == 1:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 1,  # membership id. Buying standard (id=1) here
                "membership_duration": 3,  # 3 months

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_basket_cookie", "vertex_account_cookie"],
                "exp_cookie_values": {"vertex_basket_cookie": "M:1:3;A:1"},

                "exp_flash_category": "success",
                "exp_flash_message": "Standard Membership has been added to your basket."}

    # Test 2
    # M:1:1 basket, change duration of membership
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains NO activity
    # 5. Basket cookie has standard membership (type = 1, duration = 1)
    if request.param == 2:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 1,  # membership id. Buying standard (id=1) here
                "membership_duration": 6,  # 6 months

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_basket_cookie", "vertex_account_cookie"],
                "exp_cookie_values": {"vertex_basket_cookie": "M:1:6"},

                "exp_flash_category": "success",
                "exp_flash_message": "Standard Membership has been added to your basket."}

    # Test 3
    # M:1:1 basket, upgrade basket membership
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains NO activity
    # 5. Basket cookie has standard membership (type = 1, duration = 1)
    if request.param == 3:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 2,  # membership id. Buying premium (id=2) here
                "membership_duration": 6,  # 6 months

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_basket_cookie", "vertex_account_cookie"],
                "exp_cookie_values": {"vertex_basket_cookie": "M:2:6"},

                "exp_flash_category": "success",
                "exp_flash_message": "Premium Membership has been added to your basket."}

    # Test 4
    # M:2:6 basket, downgrade basket membership
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains NO activity
    # 5. Basket cookie has standard membership (type = 2, duration = 6)
    if request.param == 4:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:2:6"),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 1,  # membership id. Buying standard (id=1) here
                "membership_duration": 12,  # 12 months

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_basket_cookie", "vertex_account_cookie"],
                "exp_cookie_values": {"vertex_basket_cookie": "M:1:12"},

                "exp_flash_category": "success",
                "exp_flash_message": "Standard Membership has been added to your basket."}

    # Test 5
    # M:1:6 basket, add invalid membership (Invalid)
    # Expect basket cookie to be deleted and error flashed as message
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains NO activity
    # 5. Basket cookie has standard membership (type = 1, duration = 6)
    if request.param == 5:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:1:6"),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 3,  # invalid membership
                "membership_duration": 1,  # 1 month

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_account_cookie"],

                "exp_flash_category": "error"}

    # Test 6
    # M:1:1 basket. Add membership with duration 0 (Invalid)
    # Expect basket cookie to be deleted and error flashed as message
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains NO activity
    # 5. Basket cookie has standard membership (type = 1, duration = 6)
    if request.param == 6:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:1:6"),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 1,  # standard membership
                "membership_duration": 0,  # 0 month

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_account_cookie"],

                "exp_flash_category": "error"}

    # Test 7
    # M:1:1 basket. Add membership with negative duration (Invalid)
    # Expect basket cookie to be deleted and error flashed as message
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains NO activity
    # 5. Basket cookie has standard membership (type = 1, duration = 6)
    if request.param == 7:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:1:6"),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 1,  # standard membership
                "membership_duration": -1,  # -1 month

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_account_cookie"],

                "exp_flash_category": "error"}

    # -----------------------------------------/ ============= \----------------------------------------- #
    # ----------------------------------------| - Extra Tests - |---------------------------------------- #
    # -----------------------------------------\ ============= /----------------------------------------- #

    # Test 8
    # Has invalid basket cookie, tries to add more (Invalid)
    # Expect basket cookie to be deleted and error flashed as message
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains 9 activities (9 * type = 1)
    # 5. Basket cookie has NO membership
    if request.param == 8:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:1;A:1;A:1;A:1;A:1;A:1;A:1;A:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "buy_membership": 1,  # standard membership
                "membership_duration": 1,  # 1 month

                "exp_title": "Memberships", "exp_url": "/info/memberships",
                "exp_template_path": "/info/memberships.html",
                "exp_exist_cookies": ["session", "vertex_account_cookie"],

                "exp_flash_category": "error"}

    # Test 9
    # A:1 basket. User not logged in, tries to add <Activity 2> to basket (Invalid)
    # Expect basket cookie to be deleted
    # Expect prompt (flashed message) telling user to login
    # Expect redirection to login page
    # ------
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie contains 9 activities (9 * type = 1)
    # 5. Basket cookie has NO membership
    if request.param == 9:
        return {"mocked_return_user_response": return_not_logged_in_user_response,
                "create_basket_cookie_and_value": (True, "A:1"),
                "create_account_cookie_and_value": (False, ""),

                "buy_membership": 1,  # standard membership
                "membership_duration": 1,  # 1 month

                "exp_title": "Login", "exp_url": "/account/login",
                "exp_template_path": "/account/login_register.html",
                "exp_exist_cookies": ["session", "vertex_account_cookie"],

                "exp_flash_category": "error",
                "exp_flash_message": "login"}
