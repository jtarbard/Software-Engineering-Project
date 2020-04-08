import flask

from main.helper_functions.test_helpers.flask_signal_capturer import captured_templates

"""
<Rule '/misc/add_booking_to_basket' (OPTIONS, POST) -> basket.view_classes_post>
"""


def test_basket_view(app, test_client, mocker, basket_template_checker, populate_database, basket_view_data):
    mocked_return_user_response = basket_view_data.get("mocked_return_user_response")
    create_basket_cookie, basket_cookie_value = basket_view_data.get("create_basket_cookie_and_value",
                                                                                      (False, ""))
    create_account_cookie, account_cookie_value = basket_view_data.get("create_account_cookie_and_value", (True, "Account"))

    exp_status_code = basket_view_data.get("exp_status_code", 200)
    exp_activities = basket_view_data.get("exp_activities", [])
    exp_membership = basket_view_data.get("exp_membership", None)
    exp_basket_membership_duration = basket_view_data.get("exp_basket_membership_duration", None)
    exp_membership_discount = basket_view_data.get("exp_membership_discount", 0)

    exp_total_activity_price = basket_view_data.get("exp_total_activity_price", 0.0)
    exp_total_discounted_price = basket_view_data.get("exp_total_discounted_price", 0.0)
    exp_final_price = basket_view_data.get("exp_final_price", 0.0)

    exp_title = basket_view_data.get("exp_title")
    exp_url = basket_view_data.get("exp_url")
    exp_template_path = basket_view_data.get("exp_template_path")
    exp_exist_cookies = basket_view_data.get("exp_exist_cookies", [])

    # ------------------------------------------------------- #

    # Get objects after database is populated (and they are created)
    # TODO: Investigate why activity.activity_type is None
    # Supply user to basket_view()
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=mocked_return_user_response)
    # Populate database with simple dummy data
    populate_database(["facility", "activity_type", "activity", "membership_type",
                       "customer", "customer_with_membership", "membership_receipt", "membership"])

    # ------------------------------------------------------- #

    with captured_templates(app) as templates:

        if create_basket_cookie:
            test_client.set_cookie("localhost", "vertex_basket_cookie", basket_cookie_value)
        if create_account_cookie:
            test_client.set_cookie("localhost", "vertex_account_cookie", account_cookie_value)
        rv = test_client.get("/account/basket", follow_redirects=True)

        basket_template_checker(response=rv, request=flask.request, templates=templates, exp_title=exp_title,
                                exp_url=exp_url, exp_template_path=exp_template_path,
                                exp_exist_cookies=exp_exist_cookies,
                                exp_status_code=exp_status_code,
                                exp_activities=exp_activities,
                                exp_membership=exp_membership,
                                exp_basket_membership_duration=exp_basket_membership_duration,
                                exp_membership_discount=exp_membership_discount,
                                exp_total_activity_price=exp_total_activity_price,
                                exp_total_discounted_price=exp_total_discounted_price,
                                exp_final_price=exp_final_price)

    # ------------------------------------------------------- #

    test_client.delete_cookie("localhost", "vertex_basket_cookie")
    test_client.delete_cookie("localhost", "vertex_account_cookie")
    test_client.get("/")

    # --------------------------------- END OF THIS TEST: test_basket_view --------------------------------- #


def test_basket_delete_activity(app, test_client, mocker, basket_template_checker, populate_database, basket_delete_activity_data):

    mocked_return_user_response = basket_delete_activity_data.get("mocked_return_user_response")
    create_basket_cookie, basket_cookie_value = basket_delete_activity_data.get("create_basket_cookie_and_value", (False, ""))
    create_account_cookie, account_cookie_value = basket_delete_activity_data.get("create_account_cookie_and_value", (True, "Account"))

    post_dict = dict(update=basket_delete_activity_data.get("update_post", False),
                     booking_id=basket_delete_activity_data.get("booking_id_post", ""),
                     num_change=basket_delete_activity_data.get("num_change_post", 0),
                     delete_basket=basket_delete_activity_data.get("delete_basket_post", None))

    exp_status_code = basket_delete_activity_data.get("exp_status_code", 200)
    exp_activities = basket_delete_activity_data.get("exp_activities", [])
    exp_membership = basket_delete_activity_data.get("exp_membership", None)
    exp_basket_membership_duration = basket_delete_activity_data.get("exp_basket_membership_duration", None)
    exp_membership_discount = basket_delete_activity_data.get("exp_membership_discount", 0)

    exp_total_activity_price = basket_delete_activity_data.get("exp_total_activity_price", 0.0)
    exp_total_discounted_price = basket_delete_activity_data.get("exp_total_discounted_price", 0.0)
    exp_final_price = basket_delete_activity_data.get("exp_final_price", 0.0)

    exp_title = basket_delete_activity_data.get("exp_title")
    exp_url = basket_delete_activity_data.get("exp_url")
    exp_template_path = basket_delete_activity_data.get("exp_template_path")
    exp_exist_cookies = basket_delete_activity_data.get("exp_exist_cookies", [])

    # ------------------------------------------------------- #

    # Get objects after database is populated (and they are created)
    # TODO: Investigate why activity.activity_type is None
    # Supply user
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=mocked_return_user_response)
    # Populate database with simple dummy data
    populate_database(["facility", "activity_type", "activity", "membership_type",
                       "customer", "customer_with_membership", "membership_receipt", "membership"])

    # ------------------------------------------------------- #

    with captured_templates(app) as templates:

        if create_basket_cookie:
            test_client.set_cookie("localhost", "vertex_basket_cookie", basket_cookie_value)
        if create_account_cookie:
            test_client.set_cookie("localhost", "vertex_account_cookie", account_cookie_value)
        rv = test_client.post("/account/basket", follow_redirects=True, data=post_dict)

        basket_template_checker(response=rv, request=flask.request, templates=templates, exp_title=exp_title,
                                exp_url=exp_url, exp_template_path=exp_template_path,
                                exp_exist_cookies=exp_exist_cookies,
                                exp_status_code=exp_status_code,
                                exp_activities=exp_activities,
                                exp_membership=exp_membership,
                                exp_basket_membership_duration=exp_basket_membership_duration,
                                exp_membership_discount=exp_membership_discount,
                                exp_total_activity_price=exp_total_activity_price,
                                exp_total_discounted_price=exp_total_discounted_price,
                                exp_final_price=exp_final_price)

    # ------------------------------------------------------- #

    test_client.delete_cookie("localhost", "vertex_basket_cookie")
    test_client.delete_cookie("localhost", "vertex_account_cookie")

    # ----------------------------- END OF THIS TEST: test_basket_delete_activity ----------------------------- #


def test_basket_delete_activity_chain(app, test_client, mocker, basket_template_checker, populate_database):
    """
    Basket_Delete_Activity_Chain_Test
    GIVEN a Flask application
    WHEN delete/update button is clicked on the '/account/basket' page (POST) multiple times
    VARYING CONDITIONS 1. User is logged in (vertex_account_cookie exists)
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

    from main.helper_functions.test_helpers.database_creation import activity_objs, activity_type_objs
    from main.helper_functions.test_helpers.mocked_functions import return_customer_no_membership_with_no_response

    # ------------------------------------------------------- #

    # Preliminary Conditions

    # Get objects after database is populated (and they are created)
    # Supply user
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=return_customer_no_membership_with_no_response)
    # Populate database with simple dummy data
    populate_database(["facility", "activity_type", "activity", "membership_type",
                       "customer", "customer_with_membership", "membership_receipt", "membership"])

    # ------------------------------------------------------- #

    # Initial Condition
    # 1. Create vertex_account_cookie
    # 2. User does not have a membership
    # 3. Create vertex_basket_cookie
    # 4. Basket cookie with 9 valid activities (type = 1, 2, 3, 4, 5, 6, 7, 8, 9)
    # 5. Basket cookie with NO membership

    test_client.set_cookie("localhost", "vertex_basket_cookie", "A:1;A:2;A:3;A:4;A:5;A:6;A:7;A:8;A:9")
    test_client.set_cookie("localhost", "vertex_account_cookie", "Account")

    # ------------------------------------------------------- #

    # Expected values throughout
    exp_title = "Basket"
    exp_url = "/account/basket"
    exp_template_path = "/account/basket.html"
    exp_exist_cookies = ["vertex_basket_cookie", "vertex_account_cookie"]

    # ------------------------------------------------------- #

    # Update 1
    # Increase Activity 2 to have 2 bookings

    with captured_templates(app) as templates:
        rv = test_client.post("/account/basket", follow_redirects=True,
                              data=dict(update=True,
                                        booking_id="A:2",
                                        num_change=2))

        basket_template_checker(response=rv, request=flask.request, templates=templates,
                                exp_title=exp_title, exp_url=exp_url,
                                exp_template_path=exp_template_path,
                                exp_exist_cookies=exp_exist_cookies,
                                exp_activities={
                                    activity_objs[0]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                    activity_objs[1]: (activity_type_objs[1].hourly_activity_price*2, 2, 0.15),
                                    activity_objs[2]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                    activity_objs[3]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                    activity_objs[4]: (activity_type_objs[1].hourly_activity_price*2, 1, 0.15),
                                    activity_objs[5]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15),
                                    activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0.15),
                                    activity_objs[7]: (activity_type_objs[1].hourly_activity_price*2, 1, 0.15),
                                    activity_objs[8]: (activity_type_objs[2].hourly_activity_price*3, 1, 0.15)},
                                exp_membership=None, exp_basket_membership_duration=None, exp_membership_discount=0,
                                exp_total_activity_price=391.0,  # 10*1 * 3 * 0.85 + 20*2 * 4 * 0.85 + 30*3 * 3 * 0.85
                                exp_total_discounted_price=391.0,
                                exp_final_price=391.0)

    # Update 2
    # Remove Activity 1 (removing bulk discount for type 1)

    with captured_templates(app) as templates:
        rv = test_client.post("/account/basket", follow_redirects=True,
                              data=dict(update=True,
                                        booking_id="A:1",
                                        num_change=0))

        basket_template_checker(response=rv, request=flask.request, templates=templates,
                                exp_title=exp_title, exp_url=exp_url,
                                exp_template_path=exp_template_path,
                                exp_exist_cookies=exp_exist_cookies,
                                exp_activities={
                                    activity_objs[1]: (activity_type_objs[1].hourly_activity_price * 2, 2, 0.15),
                                    activity_objs[2]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                    activity_objs[3]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                    activity_objs[4]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                                    activity_objs[5]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                    activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                    activity_objs[7]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                                    activity_objs[8]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15)},
                                exp_membership=None, exp_basket_membership_duration=None, exp_membership_discount=0,
                                exp_total_activity_price=385.5,  # 10*1 * 2 + 20*2 * 4 * 0.85 + 30*3 * 3 * 0.85
                                exp_total_discounted_price=385.5,
                                exp_final_price=385.5)

    # Update 3
    # Decrease Activity 2 to 1 booking

    with captured_templates(app) as templates:
        rv = test_client.post("/account/basket", follow_redirects=True,
                              data=dict(update=True,
                                        booking_id="A:2",
                                        num_change=1))

        basket_template_checker(response=rv, request=flask.request, templates=templates,
                                exp_title=exp_title, exp_url=exp_url,
                                exp_template_path=exp_template_path,
                                exp_exist_cookies=exp_exist_cookies,
                                exp_activities={
                                    activity_objs[1]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                                    activity_objs[2]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                    activity_objs[3]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                    activity_objs[4]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                                    activity_objs[5]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15),
                                    activity_objs[6]: (activity_type_objs[0].hourly_activity_price, 1, 0),
                                    activity_objs[7]: (activity_type_objs[1].hourly_activity_price * 2, 1, 0.15),
                                    activity_objs[8]: (activity_type_objs[2].hourly_activity_price * 3, 1, 0.15)},
                                exp_membership=None, exp_basket_membership_duration=None, exp_membership_discount=0,
                                exp_total_activity_price=351.5,  # 10*1 * 2 + 20*2 * 3 * 0.85 + 30*3 * 3 * 0.85
                                exp_total_discounted_price=351.5,
                                exp_final_price=351.5)

    # Update 4
    # Delete all basket items

    with captured_templates(app) as templates:
        rv = test_client.post("/account/basket", follow_redirects=True,
                              data=dict(update=True,
                                        booking_id="A:2",
                                        num_change=1,
                                        delete_basket=True))

        basket_template_checker(response=rv, request=flask.request, templates=templates,
                                exp_title=exp_title, exp_url=exp_url,
                                exp_template_path=exp_template_path,
                                exp_exist_cookies=["vertex_account_cookie"],
                                exp_activities=dict(),
                                exp_membership=None, exp_basket_membership_duration=None, exp_membership_discount=0,
                                exp_total_activity_price=0.0,
                                exp_total_discounted_price=0.0,
                                exp_final_price=0.0)

    # ------------------------------------------------------- #

    test_client.delete_cookie("localhost", "vertex_basket_cookie")
    test_client.delete_cookie("localhost", "vertex_account_cookie")

    # ----------------------------- END OF THIS TEST: test_basket_delete_activity_chain_delete ----------------------------- #


def test_view_classes_post(app, test_client, mocker, basket_template_checker, populate_database):
    assert False
