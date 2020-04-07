import datetime
import pytest


def pytest_generate_tests(metafunc):
    if "basket_view_basic_data" in metafunc.fixturenames:
        metafunc.parametrize("basket_view_basic_data", range(23), indirect=True,
                             ids=["no_basket_cookie",
                                  "A:1",
                                  "A:1;A:2;A:3",
                                  "M:1:1",
                                  "M:1:12",
                                  "A:1;M:1:1",
                                  "A:1;M:2:1",
                                  "empty basket cookie",
                                  "Multi-buy: A:3;A:3;A:3",
                                  "Pure bulk buy: A:3;A:6;A:9",
                                  "Bulk buy mix normal buy: A:2;A:2;A:5;A:3;A:6;A:9",
                                  "Pure bulk buy with membership: A:3;A:6;A:9;M:1:1",
                                  "Pure bulk buy with membership: A:3;A:6;A:9;M:2:1",
                                  "Pre-existing membership + A:1",
                                  "Pre-existing membership + A:1;A:2;A:3",
                                  "Pre-existing membership + A:1",
                                  "Pre-existing membership + A:1;A:2;A:3",
                                  "Removes overly booked activities: A:13;A:13;A:13;A:13;A:13",
                                  "User logged out, expects to be redirected to login page",
                                  "User logged out, expects to be redirected to login page and basket cookie deleted",
                                  "Floating point arithmetic test 1",
                                  "Floating point arithmetic test 2",
                                  "Floating point arithmetic test 3"])
    if "basket_delete_activity_basic_data" in metafunc.fixturenames:
        metafunc.parametrize("basket_delete_activity_basic_data", range(1), indirect=True, ids=[])


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

    data = list()

    # Test_0
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie does NOT exist
    data.append((return_customer_no_membership_with_no_response,
                 (False, ""),
                 (True, "Account"),
                 dict(),
                 None, None, 0,
                 0.0, 0.0, 0.0,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_account_cookie"]))

    # Test_1
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:1"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                 None, None, 0,
                 10.0, 10.0, 10.0,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_2
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, hourly price = 10, hour = 1), (type = 2, hourly price = 20, hour = 2), (type = 3, hourly price = 30, hour = 3)
    # 5. Basket cookie with NO valid membership exist
    exp_basket_membership_duration = 1
    exp_total_activity_price = 140.0  # 10 + 20*2 + 30*3

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:1;A:2;A:3"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                  activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                  activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0)},
                 None, None, 0,
                 exp_total_activity_price, exp_total_activity_price, exp_total_activity_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_3
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with NO activities
    # 5. Basket cookie with 1 valid membership (type = 1, duration = 1, monthly_price = 3, discount = 30(%)) exist
    exp_basket_membership_duration = 1
    exp_membership_type = membership_type_objs[0]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 0.0
    exp_total_discounted_price = 0.0
    exp_final_price = 3.0  # 3*1
    data.append((return_customer_no_membership_with_no_response,
                 (True, "M:1:1"),
                 (True, "Account"),
                 dict(),
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_4
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with NO activities
    # 5. Basket cookie with 1 valid membership (type = 1, duration = 12, monthly_price = 3, discount = 30(%)) exist
    exp_basket_membership_duration = 12
    exp_membership_type = membership_type_objs[0]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 0.0
    exp_total_discounted_price = 0.0
    exp_final_price = 36.0  # 3*12
    data.append((return_customer_no_membership_with_no_response,
                 (True, "M:1:12"),
                 (True, "Account"),
                 dict(),
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_5
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1)
    # 5. Basket cookie with 1 valid membership (type = 1, duration = 1, monthly_price = 3, discount = 30(%)) exist
    exp_basket_membership_duration = 1
    exp_membership_type = membership_type_objs[0]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 10.0
    exp_total_discounted_price = 7.0  # 10 * 0.7
    exp_final_price = 10.0  # 7.0 (activity price after membership discount) + 3.0*1 (membership price for 1 month)

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:1;M:1:1"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_6
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1)
    # 5. Basket cookie with 1 valid membership (type = 2, duration = 1, monthly_price = 10, discount = 100(%)) exist
    exp_basket_membership_duration = 1
    exp_membership_type = membership_type_objs[1]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 10.0
    exp_total_discounted_price = 0.0  # 10*0
    exp_final_price = 10.0  # 0 + 10*1 (membership price for a month)

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:1;M:2:1"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_7
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. vertex_basket_cookie is empty
    data.append((return_customer_no_membership_with_no_response,
                 (True, ""),
                 (True, "Account"),
                 dict(),
                 None, None, 0,
                 0.0, 0.0, 0.0,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_account_cookie"]))

    # Test_8 - Buying multiples of the same session should not apply "bulk buy" discount
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3x 1 valid activity (type = 3, hourly = 30, duration = 3)
    # 5. Basket cookie with NO membership
    exp_total_activity_price = 270.0  # 30*3 * 3

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:3;A:3;A:3"),
                 (True, "Account"),
                 {activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 3, 0)},
                 None, None, 0,
                 exp_total_activity_price, exp_total_activity_price, exp_total_activity_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_9 - Pure Bulk buy - 3 times = 0.15x discount
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 3, 6, 9, hourly = 30, duration = 3)
    # 5. Basket cookie with NO membership
    exp_total_activity_price = 229.5  # bulk discount on activities only. 30*3 * 3 * 0.85
    exp_total_discounted_price = 229.5  # bulk discount and membership discount.30*3 * 3 * 0.85

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:3;A:6;A:9"),
                 (True, "Account"),
                 {activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                 None, None, 0,
                 exp_total_activity_price, exp_total_discounted_price, exp_total_discounted_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_10 - Bulk buy 1 kind - 3 times = 0.85x discount, normal buy others (Testing bulk buy does not affect globally)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3x1 + 3 valid activity (type = 2, 2, 5, 3, 6, 9)
    # 5. Basket cookie with NO membership
    exp_total_activity_price = 349.5  # bulk discount on activities only. (20*2 * 3) + (30*3 * 3 * 0.85)
    exp_total_discounted_price = 349.5  # bulk discount and membership discount. (20*2 * 3) + (30*3 * 3 * 0.85)

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:2;A:2;A:5;A:3;A:6;A:9"),
                 (True, "Account"),
                 {activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 2, 0),
                  activity_objs[4]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                  activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                 None, None, 0,
                 exp_total_activity_price, exp_total_discounted_price, exp_total_discounted_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_11 - Pure Bulk buy (0.85x) with standard membership (0.7x)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 3, 6, 9)
    # 5. Basket cookie with standard membership (type = 1, monthly price = 3, duration = 1)
    exp_basket_membership_duration = 1
    exp_membership_type = membership_type_objs[0]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 229.5  # bulk discount on activities only. (30*3 * 3 * 0.85)
    exp_total_discounted_price = 160.65  # bulk discount and membership discount. (30*3 * 3 * 0.85) * 0.7
    exp_final_price = round(exp_total_discounted_price + exp_membership_type.monthly_price * exp_basket_membership_duration, 2)

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:3;A:6;A:9;M:1:1"),
                 (True, "Account"),
                 {activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_12 - Pure Bulk buy (0.85x) with premium membership (0.0x)
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 3, 6, 9)
    # 5. Basket cookie with premium membership (type = 2, monthly price = 10, duration = 1)
    exp_basket_membership_duration = 1
    exp_membership_type = membership_type_objs[1]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 229.5  # bulk discount on activities only  (30*3 * 3 * 0.85)
    exp_total_discounted_price = 0.0  # bulk discount and membership discount  (30*3 * 3 * 0.85) * 0.0
    exp_final_price = 10.0  # 0 + 10

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:3;A:6;A:9;M:2:1"),
                 (True, "Account"),
                 {activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_13
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing standard membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    exp_membership_discount = membership_type_objs[0].discount  # 30, retrieved from customer
    exp_total_activity_price = 10.0  # (10*1)
    exp_total_discounted_price = 7.0  # bulk discount and membership discount  10 * 0.7
    exp_final_price = 7.0  # no membership in basket. just pay for activities

    data.append((return_customer_standard_with_no_response,
                 (True, "A:1"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                 None, None, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_14
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing standard membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, hourly price = 10, hour = 1), (type = 2, hourly price = 20, hour = 2), (type = 3, hourly price = 30, hour = 3)
    # 5. Basket cookie with NO valid membership exist
    exp_membership_discount = membership_type_objs[0].discount  # 30, retrieved from customer
    exp_total_activity_price = 140.0  # (10 + 20*2 + 30*3)
    exp_total_discounted_price = 98.0  # bulk discount and membership discount  140 * 0.7
    exp_final_price = 98.0  # no membership in basket. just pay for activities

    data.append((return_customer_standard_with_no_response,
                 (True, "A:1;A:2;A:3"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                  activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                  activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0)},
                 None, None, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_15
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing premium membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    exp_membership_discount = membership_type_objs[1].discount  # 100, retrieved from customer
    exp_total_activity_price = 10.0  # (10*1)
    exp_total_discounted_price = 0.0  # bulk discount and membership discount  10 * 0
    exp_final_price = 0.0  # no membership in basket and has premium membership, so don't need to pay for anything

    data.append((return_customer_premium_with_no_response,
                 (True, "A:1"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0)},
                 None, None, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_16
    # 1. vertex_account_cookie exists
    # 2. User has pre-existing premium membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 1, hourly price = 10, hour = 1), (type = 2, hourly price = 20, hour = 2), (type = 3, hourly price = 30, hour = 3)
    # 5. Basket cookie with NO valid membership exist
    exp_membership_discount = membership_type_objs[1].discount  # 100, retrieved from customer
    exp_total_activity_price = 140.0  # (10 + 20*2 + 30*3)
    exp_total_discounted_price = 0.0  # bulk discount and membership discount  140 * 0.7
    exp_final_price = 0.0  # no membership in basket and has premium membership, so don't need to pay for anything

    data.append((return_customer_premium_with_no_response,
                 (True, "A:1;A:2;A:3"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                  activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0),
                  activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0)},
                 None, None, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_17 - Removes overly booked activities
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 5 valid activity (type = 13, 13, 13, 13, 13)  <<< Maximum capacity on that activity is 3
    # 5. Basket cookie with NO membership
    exp_total_activity_price = 3000.0  # (1000*3)
    exp_total_discounted_price = 3000.0  # no membership, no further discount
    exp_final_price = 3000.0  # just pay for the activities

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:13;A:13;A:13;A:13;A:13"),
                 (True, "Account"),
                 {activity_objs[13]: (activity_type_objs[4].hourly_activity_price, 3, 0)},
                 None, None, 0,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_18 - User logged out, expects to be redirected to login page
    # 1. vertex_account_cookie does NOT exist
    # 2. vertex_basket_cookie does NOT exist

    data.append((return_not_logged_in_user_response,
                 (False, ""),
                 (False, ""),
                 dict(),
                 None, None, 0,
                 0, 0, 0,
                 "Login", "/account/login", "/account/login_register.html",
                 []))

    # Test_19 - User logged out, expects to be redirected to login page (expects basket cookie to be deleted)
    # 1. vertex_account_cookie does NOT exist
    # 2. vertex_basket_cookie exists
    # 3. Basket cookie has NO activity
    # 4. Basket cookie has 1 valid membership (type = 1, monthly price = 3, duration = 3)

    data.append((return_not_logged_in_user_response,
                 (True, "M:1:1"),
                 (False, ""),
                 dict(),
                 None, None, 0,
                 0, 0, 0,
                 "Login", "/account/login", "/account/login_register.html",
                 []))

    # Test_20 - Floating point arithmetic stress test 1
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 15 valid activity (type = 1, 2, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9)
    # 5. Basket cookie with standard membership (type = 1, monthly price = 3, duration = 12)
    exp_basket_membership_duration = 12
    exp_membership_type = membership_type_objs[0]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 595.0  # bulk discount on activities only. 10*5*0.85 + 20*2*5*0.85 + 30*3*5*0.85
    exp_total_discounted_price = 416.5  # bulk discount and membership discount  595*0.7
    exp_final_price = 452.5  # 416.5+3*12

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:1;A:2;A:3;A:4;A:4;A:5;A:5;A:6;A:6;A:7;A:7;A:8;A:8;A:9;A:9;M:1:12"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                  activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 1, 0.15),
                  activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                  activity_objs[3]: (activity_type_objs[0].hourly_activity_price, 2, 0.15),
                  activity_objs[4]: (activity_type_objs[1].hourly_activity_price*2, 2, 0.15),
                  activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 2, 0.15),
                  activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 2, 0.15),
                  activity_objs[7]: (activity_type_objs[1].hourly_activity_price*2, 2, 0.15),
                  activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 2, 0.15)},
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html", ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_21 - Floating point arithmetic stress test 2
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 15 valid activity (type = 1, 2, 3, 4, 5, 6, 7, 8, 9, 6*10)
    # 5. Basket cookie with standard membership (type = 1, monthly price = 3, duration = 12)
    exp_basket_membership_duration = 12
    exp_membership_type = membership_type_objs[0]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 357.00066666  # bulk discount on activities only. 10*3*0.85 + 20*2*3*0.85 + 30*3*3*0.85 + 0.00011111*6
    exp_total_discounted_price = 249.900466662  # bulk discount and membership discount  357.00066666*0.7
    exp_final_price = 285.900466662  # 249.900466662+3*12

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:1;A:2;A:3;A:4;A:5;A:6;A:7;A:8;A:9;A:10;A:10;A:10;A:10;A:10;A:10;M:1:12"),
                 (True, "Account"),
                 {activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                  activity_objs[1]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                  activity_objs[2]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                  activity_objs[3]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                  activity_objs[4]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                  activity_objs[5]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                  activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                  activity_objs[7]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                  activity_objs[8]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                  activity_objs[9]: (0.00011111, 6, 0)},
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html",
                 ["vertex_basket_cookie", "vertex_account_cookie"]))

    # Test_22 - Floating point arithmetic stress test 3
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 3 valid activity (type = 10, 11, 12)
    # 5. Basket cookie with standard membership (type = 1, monthly price = 3, duration = 1)
    exp_basket_membership_duration = 1
    exp_membership_type = membership_type_objs[0]
    exp_membership_discount = exp_membership_type.discount
    exp_total_activity_price = 0.0002833305  # bulk discount on activities only. 0.00011111*3 * 0.85
    exp_total_discounted_price = 0.00019833135  # bulk discount and membership discount  0.0002833305*0.7
    exp_final_price = 3.00019833135  # 0.00019833135+3*1

    data.append((return_customer_no_membership_with_no_response,
                 (True, "A:10;A:11;A:12;M:1:1"),
                 (True, "Account"),
                 {activity_objs[9]: (0.00011111, 1, 0.15),
                  activity_objs[10]: (0.00011111, 1, 0.15),
                  activity_objs[11]: (0.00011111, 1, 0.15)},
                 exp_membership_type, exp_basket_membership_duration, exp_membership_discount,
                 exp_total_activity_price, exp_total_discounted_price, exp_final_price,
                 "Basket", "/account/basket", "/account/basket.html",
                 ["vertex_basket_cookie", "vertex_account_cookie"]))

    return data[request.param]


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

    # Test_0 - basic increase
    # 1. vertex_account_cookie exists
    # 2. User does not have a membership
    # 3. vertex_basket_cookie exists
    # 4. Basket cookie with 1 valid activity (type = 1, hourly price = 10, hour = 1) exist
    # 5. Basket cookie with NO memberships
    pass
