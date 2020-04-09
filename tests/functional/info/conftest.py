import pytest


def pytest_generate_tests(metafunc):
    if "membership_view_data" in metafunc.fixturenames:
        metafunc.parametrize("membership_view_data", range(5), indirect=True,
                             ids=["[Basic] Not logged in, No membership",
                                  "[Basic] Logged in, No membership",
                                  "[Basic] Logged in, standard membership",
                                  "[Basic] Logged in, premium membership",
                                  "[Extra] Basket cookie is retained and unmodified"])


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
