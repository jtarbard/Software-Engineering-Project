import datetime
import pytest


def pytest_generate_tests(metafunc):
    if "basket_view_basic_data" in metafunc.fixturenames:
        metafunc.parametrize("basket_view_basic_data", range(23), indirect=True,
                             ids=["[BASIC] no_basket_cookie",
                                  "[BASIC] A:1",
                                  "[BASIC] A:1;A:2;A:3",
                                  "[BASIC] M:1:1",
                                  "[BASIC] M:1:12",
                                  "[BASIC] A:1;M:1:1",
                                  "[BASIC] A:1;M:2:1",
                                  "[BASIC] Multi-buy: A:3;A:3;A:3",
                                  "[BASIC] Pure bulk buy: A:3;A:6;A:9",
                                  "[BASIC] Bulk buy mix normal buy: A:2;A:2;A:5;A:3;A:6;A:9",
                                  "[BASIC] Pure bulk buy with membership: A:3;A:6;A:9;M:1:1",
                                  "[BASIC] Pure bulk buy with membership: A:3;A:6;A:9;M:2:1",
                                  "[BASIC] Pre-existing membership + A:1",
                                  "[BASIC] Pre-existing membership + A:1;A:2;A:3",
                                  "[BASIC] Pre-existing membership + A:1",
                                  "[BASIC] Pre-existing membership + A:1;A:2;A:3",
                                  "[BASIC] User logged out, expects to be redirected to login page",
                                  "[BASIC] User logged out, expects to be redirected to login page and basket cookie deleted",
                                  "[EXTRA] empty basket cookie",  # TODO: Define behaviour when cookie failed to decode
                                  "[EXTRA] Removes overly booked activities: A:13;A:13;A:13;A:13;A:13",
                                  "[EXTRA] Floating point arithmetic test 1",
                                  "[EXTRA] Floating point arithmetic test 2",
                                  "[EXTRA] Floating point arithmetic test 3"])
    if "basket_delete_activity_basic_data" in metafunc.fixturenames:
        metafunc.parametrize("basket_delete_activity_basic_data", range(22), indirect=True,
                             ids=["[BASIC] basic increase",
                                  "[BASIC] basic decrease",
                                  "[BASIC] update specific activity among a bunch of bookings",
                                  "[BASIC] Remove activity, basket non empty",
                                  "[BASIC] Remove activity, empties basket as a result (expects basket cookie to be destroyed)",
                                  "[BASIC] Remove activity, still retaining regular discount",
                                  "[BASIC] Remove activity, disqualifying regular discount as a result (No membership)",
                                  "[BASIC] Remove activity, disqualifying regular discount as a result (Basket membership)",
                                  "[BASIC] Remove activity, disqualifying regular discount as a result (Pre-existing standard membership). 0.7x",
                                  "[BASIC] Remove activity, disqualifying regular discount as a result (Pre-existing premium membership). 0.0x",
                                  "[BASIC] Delete all items button",
                                  "[BASIC] Negative number of bookings",
                                  "[BASIC] Over 8 bookings for a single activity via Update",
                                  "[BASIC] booking_id of invalid format",
                                  "[BASIC] Change booking number so that it exceeds the maximum bookings per receipt allowed (15) - 2 activities",
                                  "[BASIC] Change booking number so that it exceeds the maximum bookings per receipt allowed (15) - 15 activities",
                                  "[EXTRA] Increases membership duration",
                                  "[EXTRA] Decreases membership duration",
                                  "[EXTRA] Setting membership duration as 0 in attempt to remove it",
                                  "[EXTRA] creating new bookings via update",
                                  "[EXTRA] replace membership via update (This is currently impossible)",
                                  "[EXTRA] user not logged in. Expect to clear basket cookie and redirect to login page"])


@pytest.fixture
def basket_view_basic_data(request):
    from tests.helper.database_creation import activity_objs, activity_type_objs, membership_type_objs
    from tests.helper.mocked_functions import return_customer_no_membership_with_no_response, \
        return_customer_premium_with_no_response, \
        return_customer_standard_with_no_response, \
        return_not_logged_in_user_response

    """
    Basket_View_Basic_Test
    GIVEN a Flask application
    WHEN the '/account/basket' page is requested (GET)
    VARYING CONDITIONS 1. User with/without membership is logged in / not logged in (vertex_account_cookie exists or not)
                       2. Basket cookie with ? valid activity
                       3. Basket cookie with ? membership
    THEN check 1. Valid status code (200)
               2. The redirected url
               3. page_title (rendered template parameter) or actual page title
               4. name of the rendered template
               5. Existing cookies
               6. Here we will rely on the cookie being correctly decoded (Yes this is bad and depends on another
                  function, but for the convenience of setting 3 test input data with a single string is irresistible...
                  However, ensuring the cookie is correctly decoded is NOT the focus here.) Check that:
                  a. basket_activities returns accordingly
                  b. basket_membership returns accordingly
                  c. basket_membership_duration returns accordingly
               7. current_membership_discount returns accordingly (depends on basket / user owned membership)
               8. total_activity_price is calculated correctly (subtotal of all activity prices, without discounts)
               9. total_discounted_price is calculated correctly (subtotal of all activity prices, after discount)
               10. activity_and_price (a dict) returns accordingly:
                   a. All keys (activity objs) exist in the expected activity objs dict key set (exp_activities)
                   b. For each activity object, the hourly activity price is correctly retrieved
                   c. For each activity object, the number of bookings for that activity is correctly summed up
                   d. For each activity object, the bulk discount due to the number of bookings for that activity is correctly returned
               11. final_price is calculated correctly (sum of total_discounted_price and membership_price)

    TESTING FOR <Rule '/account/basket' (OPTIONS, HEAD, GET) -> basket.basket_view>
    """

    # TODO: Consider refactoring the data in another function so that "data" doesn't need to be re-run n times.
    #       Have 2 functions as "Data Container" and "Data Retrieval"
    # mocked_return_user_response,
    # (create_basket_cookie, basket_cookie_value),
    # (create_account_cookie, account_cookie_value),
    # exp_activities,
    # exp_membership, exp_basket_membership_duration, exp_membership_discount,
    # exp_total_activity_price, exp_total_discounted_price, exp_final_price,
    # exp_title, exp_url, exp_template_path, exp_exist_cookies = basket_view_basic_data

    # Test_0
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie does NOT exist
    if request.param == 0:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (False, ""),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": dict(),
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 0.0,
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_account_cookie"]}

    # Test_1
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    elif request.param == 1:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 10.0,
                "exp_total_discounted_price": 10.0,
                "exp_final_price": 10.0,
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_2
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, hourly price = 10, hour = 1), (type = 2, hourly price = 20, hour = 2), (type = 3, hourly price = 30, hour = 3)
    # 5. Basket cookie with NO valid membership exist
    elif request.param == 2:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                   activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                                   activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 140.0,  # 10 + 20*2 + 30*3
                "exp_total_discounted_price": 140.0,
                "exp_final_price": 140.0,
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_3
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with NO activities
    # 5. Basket cookie with 1 valid membership (type = 1, duration = 1, monthly_price = 3, discount = 30(%)) exist
    elif request.param == 3:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": dict(),
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 1,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 3.0,  # 3*1
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_4
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with NO activities
    # 5. Basket cookie with 1 valid membership (type = 1, duration = 12, monthly_price = 3, discount = 30(%)) exist
    elif request.param == 4:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:1:12"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": dict(),
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 12,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 36.0,  # 3*12
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_5
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1)
    # 5. Basket cookie with 1 valid membership (type = 1, duration = 1, monthly_price = 3, discount = 30(%)) exist
    elif request.param == 5:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 1,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 10.0,
                "exp_total_discounted_price": 7.0,  # 10 * 0.7
                "exp_final_price": 10.0,  # 7.0 (activity price after membership discount) + 3.0*1 (membership price for 1 month)
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_6
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1)
    # 5. Basket cookie with 1 valid membership (type = 2, duration = 1, monthly_price = 10, discount = 100(%)) exist
    elif request.param == 6:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;M:2:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": membership_type_objs[1], "exp_basket_membership_duration": 1,
                "exp_membership_discount": membership_type_objs[1].discount,
                "exp_total_activity_price": 10.0,
                "exp_total_discounted_price": 0.0,  # 10 * 0.0
                "exp_final_price": 10.0,  # 0 + 10*1 (membership price for a month)
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_7 - Buying multiples of the same session should not apply "bulk buy" discount
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3x 1 valid activity (type = 3, hourly = 30, duration = 3)
    # 5. Basket cookie with NO membership
    elif request.param == 7:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:3;A:3;A:3"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 3, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 270.0,  # 30*3 * 3
                "exp_total_discounted_price": 270.0,
                "exp_final_price": 270.0,
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_8 - Pure Bulk buy - 3 times = 0.15x discount
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 3, 6, 9, hourly = 30, duration = 3)
    # 5. Basket cookie with NO membership
    elif request.param == 8:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:3;A:6;A:9"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 229.5,  # bulk discount on activities only. 30*3 * 3 * 0.85
                "exp_total_discounted_price": 229.5,  # bulk discount and membership discount.30*3 * 3 * 0.85
                "exp_final_price": 229.5,
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_9 - Bulk buy 1 kind - 3 times = 0.85x discount, normal buy others (Testing bulk buy does not affect globally)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3x1 + 3 valid activity (type = 2, 2, 5, 3, 6, 9)
    # 5. Basket cookie with NO membership
    elif request.param == 9:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:2;A:2;A:5;A:3;A:6;A:9"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 2, 0),
                                   activity_objs[4]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                                   activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 349.5,  # bulk discount on activities only. (20*2 * 3) + (30*3 * 3 * 0.85)
                "exp_total_discounted_price": 349.5,  # bulk discount and membership discount. (20*2 * 3) + (30*3 * 3 * 0.85)
                "exp_final_price": 349.5,
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_10 - Pure Bulk buy (0.85x) with standard membership (0.7x)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 3, 6, 9)
    # 5. Basket cookie with standard membership (type = 1, monthly price = 3, duration = 1)
    elif request.param == 10:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:3;A:6;A:9;M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 1,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 229.5,  # bulk discount on activities only. (30*3 * 3 * 0.85)
                "exp_total_discounted_price": 160.65,  # bulk discount and membership discount. (30*3 * 3 * 0.85) * 0.7
                "exp_final_price": 163.65,  # 160.65 + 3*1
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_11 - Pure Bulk buy (0.85x) with premium membership (0.0x)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 3, 6, 9)
    # 5. Basket cookie with premium membership (type = 2, monthly price = 10, duration = 1)
    elif request.param == 11:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:3;A:6;A:9;M:2:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[2]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                   activity_objs[5]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                   activity_objs[8]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15)},
                "exp_membership": membership_type_objs[1], "exp_basket_membership_duration": 1,
                "exp_membership_discount": membership_type_objs[1].discount,
                "exp_total_activity_price": 229.5,  # bulk discount on activities only  (30*3 * 3 * 0.85)
                "exp_total_discounted_price": 0.0,  # bulk discount and membership discount  (30*3 * 3 * 0.85) * 0.0
                "exp_final_price": 10.0,  # 0 + 10
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_12
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing standard membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    elif request.param == 12:
        return {"mocked_return_user_response": return_customer_standard_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None,
                "exp_membership_discount": membership_type_objs[0].discount,  # 30, retrieved from customer
                "exp_total_activity_price": 10.0,  # (10*1)
                "exp_total_discounted_price": 7.0,  # bulk discount and membership discount  10 * 0.7
                "exp_final_price": 7.0,  # no membership in basket. just pay for activities
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_13
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing standard membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, hourly price = 10, hour = 1), (type = 2, hourly price = 20, hour = 2), (type = 3, hourly price = 30, hour = 3)
    # 5. Basket cookie with NO valid membership exist
    elif request.param == 13:
        return {"mocked_return_user_response": return_customer_standard_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                   activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                                   activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None,
                "exp_membership_discount": membership_type_objs[0].discount,  # 30, retrieved from customer
                "exp_total_activity_price": 140.0,  # (10 + 20*2 + 30*3)
                "exp_total_discounted_price": 98.0,  # bulk discount and membership discount  140 * 0.7
                "exp_final_price": 98.0,  # no membership in basket. just pay for activities
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_14
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing premium membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    elif request.param == 14:
        return {"mocked_return_user_response": return_customer_premium_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None,
                "exp_membership_discount": membership_type_objs[1].discount,  # 100, retrieved from customer
                "exp_total_activity_price": 10.0,  # (10*1)
                "exp_total_discounted_price": 0.0,  # bulk discount and membership discount  10 * 0.0
                "exp_final_price": 0.0,  # no membership in basket and has premium membership, so don't need to pay for anything
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_15
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing premium membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, hourly price = 10, hour = 1), (type = 2, hourly price = 20, hour = 2), (type = 3, hourly price = 30, hour = 3)
    # 5. Basket cookie with NO valid membership exist
    elif request.param == 15:
        return {"mocked_return_user_response": return_customer_premium_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                   activity_objs[1]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0),
                                   activity_objs[2]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None,
                "exp_membership_discount": membership_type_objs[1].discount,  # 100, retrieved from customer
                "exp_total_activity_price": 140.0,  # (10 + 20*2 + 30*3)
                "exp_total_discounted_price": 0.0,  # bulk discount and membership discount  140 * 0.7
                "exp_final_price": 0.0,  # no membership in basket and has premium membership, so don't need to pay for anything
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_16 - User logged out, expects to be redirected to login page
    # 1. vertex_account_cookie does NOT exist
    # 2. vertex_basket_cookie does NOT exist
    elif request.param == 16:
        return {"mocked_return_user_response": return_not_logged_in_user_response,
                "create_basket_cookie_and_value": (False, ""),
                "create_account_cookie_and_value": (False, ""),

                "exp_activities": dict(),
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "Login", "exp_url": "/account/login",
                "exp_template_path": "/account/login_register.html",
                "exp_exist_cookies": []}

    # Test_17 - User logged out, expects to be redirected to login page (expects basket cookie to be deleted)
    # 1. vertex_account_cookie does NOT exist
    # 2. vertex_basket_cookie exists
    # 3. Basket cookie has NO activity
    # 4. Basket cookie has 1 valid membership (type = 1, monthly price = 3, duration = 3)
    elif request.param == 17:
        return {"mocked_return_user_response": return_not_logged_in_user_response,
                "create_basket_cookie_and_value": (True, "M:1:1"),
                "create_account_cookie_and_value": (False, ""),

                "exp_activities": dict(),
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "Login", "exp_url": "/account/login",
                "exp_template_path": "/account/login_register.html",
                "exp_exist_cookies": []}

    # -----------------------------------------/ ============= \----------------------------------------- #
    # ----------------------------------------| - Extra Tests - |---------------------------------------- #
    # -----------------------------------------\ ============= /----------------------------------------- #

    # Test_18 - empty basket cookie
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. vertex_basket_cookie is empty
    elif request.param == 18:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, ""),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": dict(),
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 0.0,
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_account_cookie"]}

    # Test_19 - Removes overly booked activities
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 5 valid activity (type = 13, 13, 13, 13, 13)  <<< Maximum capacity on that activity is 3
    # 5. Basket cookie with NO membership
    elif request.param == 19:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:13;A:13;A:13;A:13;A:13"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[13]: (activity_type_objs[4].hourly_activity_price, 3, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 3000.0,  # (1000*3)
                "exp_total_discounted_price": 3000.0,  # no membership, no further discount
                "exp_final_price": 3000.0,  # just pay for the activities
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_20 - Floating point arithmetic stress test 1
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 15 valid activity (type = 1, 2, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9)
    # 5. Basket cookie with standard membership (type = 1, monthly price = 3, duration = 12)
    elif request.param == 20:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3;A:4;A:4;A:5;A:5;A:6;A:6;A:7;A:7;A:8;A:8;A:9;A:9;M:1:12"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                   activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0.15),
                                   activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[3]: (activity_type_objs[0].hourly_activity_price, 2, 0.15),
                                   activity_objs[4]: (activity_type_objs[1].hourly_activity_price*2, 2, 0.15),
                                   activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 2, 0.15),
                                   activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 2, 0.15),
                                   activity_objs[7]: (activity_type_objs[1].hourly_activity_price*2, 2, 0.15),
                                   activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 2, 0.15)},
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 12,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 595.0,  # bulk discount on activities only. 10*5*0.85 + 20*2*5*0.85 + 30*3*5*0.85
                "exp_total_discounted_price": 416.5,  # bulk discount and membership discount  595*0.7
                "exp_final_price": 452.5,  # 416.5+3*12
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_21 - Floating point arithmetic stress test 2
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 15 valid activity (type = 1, 2, 3, 4, 5, 6, 7, 8, 9, 6*10)
    # 5. Basket cookie with standard membership (type = 1, monthly price = 3, duration = 12)
    elif request.param == 21:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3;A:4;A:5;A:6;A:7;A:8;A:9;A:10;A:10;A:10;A:10;A:10;A:10;M:1:12"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                   activity_objs[1]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                                   activity_objs[2]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                   activity_objs[3]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                   activity_objs[4]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                                   activity_objs[5]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                   activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                   activity_objs[7]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                                   activity_objs[8]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                   activity_objs[9]: (0.00011111, 6, 0)},
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 12,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 357.00066666,  # bulk discount on activities only. 10*3*0.85 + 20*2*3*0.85 + 30*3*3*0.85 + 0.00011111*6
                "exp_total_discounted_price": 249.900466662,  # bulk discount and membership discount  357.00066666*0.7
                "exp_final_price": 285.900466662,  # 249.900466662+3*12
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_22 - Floating point arithmetic stress test 3
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 10, 11, 12)
    # 5. Basket cookie with standard membership (type = 1, monthly price = 3, duration = 1)
    elif request.param == 22:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:10;A:11;A:12;M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "exp_activities": {activity_objs[9]: (0.00011111, 1, 0.15),
                                   activity_objs[10]: (0.00011111, 1, 0.15),
                                   activity_objs[11]: (0.00011111, 1, 0.15)},
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 1,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 0.0002833305,  # bulk discount on activities only. 0.00011111*3 * 0.85
                "exp_total_discounted_price": 0.00019833135,  # bulk discount and membership discount  0.0002833305*0.7
                "exp_final_price": 3.00019833135,  # 0.00019833135+3*1
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    else:
        return False


@pytest.fixture
def basket_delete_activity_basic_data(request):
    from tests.helper.database_creation import activity_objs, activity_type_objs, membership_type_objs
    from tests.helper.mocked_functions import return_customer_no_membership_with_no_response, \
        return_customer_premium_with_no_response, \
        return_customer_standard_with_no_response, \
        return_not_logged_in_user_response

    """
    Basket_Delete_Activity_Basic_Test
    GIVEN a Flask application
    WHEN delete/update button is clicked on the '/account/basket' page (POST)
    VARYING CONDITIONS 1. User with/without membership is logged in / not logged in (vertex_account_cookie exists or not)
                       2. Basket cookie with ? valid activity
                       3. Basket cookie with ? membership
    THEN check 1. Valid status code (200)
               2. The redirected url
               3. page_title (rendered template parameter) or actual page title
               4. name of the rendered template
               5. Existing cookies
               6. Here we will rely on the cookie being correctly decoded (Yes this is bad and depends on another
                  function, but for the convenience of setting 3 test input data with a single string is irresistible...
                  However, ensuring the cookie is correctly decoded is NOT the focus here.) Check that:
                  a. basket_activities returns accordingly
                  b. basket_membership returns accordingly
                  c. basket_membership_duration returns accordingly
               7. current_membership_discount returns accordingly (depends on basket / user owned membership)
               8. total_activity_price is calculated correctly (subtotal of all activity prices, without discounts)
               9. total_discounted_price is calculated correctly (subtotal of all activity prices, after discount)
               10. activity_and_price (a dict) returns accordingly:
                   a. All keys (activity objs) exist in the expected activity objs dict key set (exp_activities)
                   b. For each activity object, the hourly activity price is correctly retrieved
                   c. For each activity object, the number of bookings for that activity is correctly summed up
                   d. For each activity object, the bulk discount due to the number of bookings for that activity is correctly returned
               11. final_price is calculated correctly (sum of total_discounted_price and membership_price)

    TESTING FOR <Rule '/account/basket' (OPTIONS, POST) -> basket.basket_delete_activity>
    """

    # -----------------------------------------| ============= |----------------------------------------- #
    # -----------------------------------------|  Basic Tests  |----------------------------------------- #
    # -----------------------------------------| ============= |----------------------------------------- #

    # Test_0 - basic increase
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    if request.param == 0:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:1",
                "num_change_post": 2,

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 2, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 20.0,
                "exp_total_discounted_price": 20.0,
                "exp_final_price": 20.0,
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_1 - basic decrease
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 2*1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    elif request.param == 1:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:1",
                "num_change_post": 1,

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 10.0,
                "exp_total_discounted_price": 10.0,
                "exp_final_price": 10.0,
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_2 - update specific activity among a bunch of bookings
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    elif request.param == 2:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3;A:5;A:6;A:9"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:1",
                "num_change_post": 3,

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 3, 0),
                                   activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                                   activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[4]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                                   activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                   activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 339.5,  # 10*3 + 20*2*2 + 30*3 * 3 * 0.85
                "exp_total_discounted_price": 339.5,
                "exp_final_price": 339.5,
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_3 - Remove activity, basket non empty
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 2 valid activity (type = 1, 2) exist
    # 5. Basket cookie with NO memberships
    elif request.param == 3:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:1",
                "num_change_post": 0,

                "exp_activities": {activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 40.0,  # 20*2
                "exp_total_discounted_price": 40.0,
                "exp_final_price": 40.0,
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_4 - Remove activity, empties basket as a result (expects basket cookie to be destroyed)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 5) exist
    # 5. Basket cookie with NO memberships
    elif request.param == 4:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:5"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:5",
                "num_change_post": 0,

                "exp_activities": dict(),
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 0.0,
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_account_cookie"]}

    # Test_5 - Remove activity, still retaining regular discount
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 4 valid activity (type = 1, 4, 7, 16) exist, activates 0.85x regular discount
    # 5. Basket cookie with NO memberships
    elif request.param == 5:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:4;A:7;A:16"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:4",
                "num_change_post": 0,

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                   activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                   activity_objs[15]: (activity_type_objs[0].hourly_activity_price, 1, 0.15)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 25.5,  # 10*3 * 0.85
                "exp_total_discounted_price": 25.5,
                "exp_final_price": 25.5,
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_6 - Remove activity, disqualifying regular discount as a result (No membership)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, 4, 7) exist, activates 0.85x regular discount (before update)
    # 5. Basket cookie with NO memberships
    elif request.param == 6:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:4;A:7"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:4",
                "num_change_post": 0,

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                   activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 20.0,  # 10+10
                "exp_total_discounted_price": 20.0,
                "exp_final_price": 20.0,
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_7 - Remove activity, disqualifying regular discount as a result (Basket membership)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, 4, 7) exist, activates 0.85x regular discount (before update)
    # 5. Basket cookie with Standard memberships (discount = 30, monthly price = 3, duration = 1)
    elif request.param == 7:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:4;A:7;M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:4",
                "num_change_post": 0,

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                   activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 1,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 20.0,  # 10+10
                "exp_total_discounted_price": 14.0,  # 20*0.7
                "exp_final_price": 17.0,  # 14+3*1
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_8 - Remove activity, disqualifying regular discount as a result (Pre-existing standard membership). 0.7x
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing Standard membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, 4, 7) exist, activates 0.85x regular discount (before update)
    # 5. Basket cookie with NO membership
    elif request.param == 8:
        return {"mocked_return_user_response": return_customer_standard_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:4;A:7"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:4",
                "num_change_post": 0,

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                   activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 20.0,  # 10+10
                "exp_total_discounted_price": 14.0,  # 20*0.7
                "exp_final_price": 14.0,  # no basket membership
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_9 - Remove activity, disqualifying regular discount as a result (Pre-existing premium membership). 0.0x
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing Premium membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, 4, 7) exist, activates 0.85x regular discount (before update)
    # 5. Basket cookie with NO memberships
    elif request.param == 9:
        return {"mocked_return_user_response": return_customer_premium_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:4;A:7"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:4",
                "num_change_post": 0,

                "exp_activities": {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                   activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                "exp_membership": None, "exp_basket_membership_duration": None,
                "exp_membership_discount": membership_type_objs[1].discount,
                "exp_total_activity_price": 20.0,  # 10+10
                "exp_total_discounted_price": 0.0,  # 20*0.0
                "exp_final_price": 0.0,  # no basket membership
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_10 - Delete all items button
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 5 valid activity (type = 1, 2, 5, 7, 7) exist
    # 5. Basket cookie with Standard memberships
    elif request.param == 10:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;M:1:12;A:2;A:5;A:7;A:7"),
                "create_account_cookie_and_value": (True, "Account"),

                "delete_basket_post": True,
                "update_post": True,
                "booking_id_post": "A:7",
                "num_change_post": 2,

                "exp_activities": dict(),
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 0.0,
                "exp_title": "Basket", "exp_url": "/account/basket",
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_account_cookie"]}

    # Test_11 - Negative number of bookings
    # (TODO: Define behaviour. Should the page throw up 500 or flash an error, then tries to remove that invalid row of booking?)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 4 valid activity (type = 4, 5, 5, 5) exist
    # 5. Basket cookie with Standard memberships (duration 1)
    elif request.param == 11:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:4;M:1:1;A:5;A:5;A:5"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:4",
                "num_change_post": -1,

                "exp_status_code": 500,
                "exp_activities": None,
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "", "exp_url": '/account/basket',
                "exp_template_path": "/misc/server_error.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_12 - Over 8 bookings for a single activity via Update
    # (TODO: Define behaviour. Should the page throw up 500 or flash an error, then tries to remove that invalid row of booking?)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 4 valid activity (type = 4, 5, 5, 5) exist
    # 5. Basket cookie with NO membership
    elif request.param == 12:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:4;A:5;A:5;A:5"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:4",
                "num_change_post": 9,

                "exp_status_code": 500,
                "exp_activities": None,
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "", "exp_url": '/account/basket',
                "exp_template_path": "/misc/server_error.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_13 - booking_id of invalid format
    # (TODO: Define behaviour. Should the page throw up 500 or flash an error, then tries to remove that invalid row of booking?)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, 2, 3) exist
    # 5. Basket cookie with NO membership
    elif request.param == 13:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:1:1",
                "num_change_post": 9,

                "exp_status_code": 500,
                "exp_activities": None,
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "", "exp_url": '/account/basket',
                "exp_template_path": "/misc/server_error.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_14 - Change booking number so that it exceeds the maximum bookings per receipt allowed (15) - 2 activities
    # (TODO: Define behaviour. Should the page throw up 500 or flash an error, then tries to remove that invalid row of booking?)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 8*1+1 valid activity (type = 8*1, 2) exist
    # 5. Basket cookie with NO membership
    elif request.param == 14:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:1;A:1;A:1;A:1;A:1;A:1;A:1;A:2"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:2",
                "num_change_post": 8,

                "exp_status_code": 500,
                "exp_activities": None,
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "", "exp_url": '/account/basket',
                "exp_template_path": "/misc/server_error.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_15 - Change booking number so that it exceeds the maximum bookings per receipt allowed (15) - 15 activities
    # (TODO: Define behaviour. Should the page throw up 500 or flash an error, then tries to remove that invalid row of booking?)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 15 valid activity (type = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15) exist
    # 5. Basket cookie with NO membership
    elif request.param == 15:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3;A:4;A:5;A:6;A:7;A:8;A:9;A:10;A:11;A:12;A:13;A:14;A:15"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:1",
                "num_change_post": 2,

                "exp_status_code": 500,
                "exp_activities": None,
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "", "exp_url": '/account/basket',
                "exp_template_path": "/misc/server_error.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # *Test_0 - Updates multiple times - difficult to generalize

    # -----------------------------------------/ ============= \----------------------------------------- #
    # ----------------------------------------| - Extra Tests - |---------------------------------------- #
    # -----------------------------------------\ ============= /----------------------------------------- #

    # Test_16 - Increases membership duration
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with NO activity
    # 5. Basket cookie with Standard membership (monthly = 3, duration = 1, discount = 30)
    elif request.param == 16:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:1:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "M:1:1",
                "num_change_post": 3,

                "exp_activities": dict(),
                "exp_membership": membership_type_objs[0], "exp_basket_membership_duration": 3,
                "exp_membership_discount": membership_type_objs[0].discount,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 9.0,  # 3*3
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_17 - Decreases membership duration
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with NO activity
    # 5. Basket cookie with Premium membership (monthly = 10, duration = 12, discount = 100)
    elif request.param == 17:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:2:12"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "M:2:12",
                "num_change_post": 6,

                "exp_activities": dict(),
                "exp_membership": membership_type_objs[1], "exp_basket_membership_duration": 6,
                "exp_membership_discount": membership_type_objs[1].discount,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 60.0,  # 10*6
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_18 - Setting membership duration as 0 in attempt to remove it
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with NO activity
    # 5. Basket cookie with Premium membership (monthly = 10, duration = 3, discount = 100)
    elif request.param == 18:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "M:2:3"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "M:2:3",
                "num_change_post": 0,

                "exp_activities": dict(),
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0.0,
                "exp_total_discounted_price": 0.0,
                "exp_final_price": 0.0,
                "exp_title": "Basket", "exp_url": '/account/basket',
                "exp_template_path": "/account/basket.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_19 - creating new bookings via update
    # TODO: Define behaviour. Throw error or allow?
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1)
    # 5. Basket cookie with NO membership
    elif request.param == 19:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1"),
                "create_account_cookie_and_value": (True, "Account"),

                "update_post": True,
                "booking_id_post": "A:2",
                "num_change_post": 1,

                "exp_status_code": 500,
                "exp_activities": None,
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "", "exp_url": '/account/basket',
                "exp_template_path": "/misc/server_error.html",
                "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_20 - replace membership via update (This is currently impossible)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with NO activity
    # 5. Basket cookie with Premium membership (monthly = 10, duration = 3, discount = 100)
    elif request.param == 20:
        return False
    #     return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
    #             "create_basket_cookie_and_value": (True, "M:2:3"),
    #             "create_account_cookie_and_value": (True, "Account"),
    #
    #             "update_post": True,
    #             "booking_id_post": "M:2:3",
    #             "num_change_post": 0,
    #
    #             "exp_activities": dict(),
    #             "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
    #             "exp_total_activity_price": 0.0,
    #             "exp_total_discounted_price": 0.0,
    #             "exp_final_price": 0.0,
    #             "exp_title": "Basket", "exp_url": '/account/basket',
    #             "exp_template_path": "/account/basket.html",
    #             "exp_exist_cookies": ["vertex_basket_cookie", "vertex_account_cookie"]}

    # Test_21 - user not logged in. Expect to clear basket cookie and redirect to login page
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activities (type = 1, 2, 3)
    # 5. Basket cookie with NO membership
    elif request.param == 21:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "create_basket_cookie_and_value": (True, "A:1;A:2;A:3"),
                "create_account_cookie_and_value": (False, ""),

                "update_post": True,
                "booking_id_post": "A:1",
                "num_change_post": 2,

                "exp_status_code": 200,
                "exp_activities": None,
                "exp_membership": None, "exp_basket_membership_duration": None, "exp_membership_discount": 0,
                "exp_total_activity_price": 0,
                "exp_total_discounted_price": 0,
                "exp_final_price": 0,
                "exp_title": "Login", "exp_url": '/account/login',
                "exp_template_path": "/account/login_register.html",
                "exp_exist_cookies": []}

    else:
        return {"mocked_return_user_response": return_customer_no_membership_with_no_response,
                "booking_id_post": "A:1",
                "num_change_post": 1,
                "exp_title": "Unknown Test Title",
                "exp_url": "Unknown Test url",
                "exp_template_path": "Unknown Test template path"}
