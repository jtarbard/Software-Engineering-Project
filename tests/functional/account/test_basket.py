import flask

from tests.helper.flask_signal_capturer import captured_templates
from tests.helper.mocked_functions import return_logged_in_user_response, return_not_logged_in_user_response

from tests.helper.database_creation import populate_database


"""
<Rule '/misc/add_booking_to_basket' (OPTIONS, POST) -> basket.view_classes_post>
"""


def test_basket_view_basic(app, test_client, mocker, basket_template_checker, populate_database, basket_view_basic_data):
    mocked_return_user_response = basket_view_basic_data.get("mocked_return_user_response")
    create_basket_cookie, basket_cookie_value = basket_view_basic_data.get("create_basket_cookie_and_value",
                                                                                      (False, ""))
    create_account_cookie, account_cookie_value = basket_view_basic_data.get("create_account_cookie_and_value", (True, "Account"))

    exp_status_code = basket_view_basic_data.get("exp_status_code", 200)
    exp_activities = basket_view_basic_data.get("exp_activities", [])
    exp_membership = basket_view_basic_data.get("exp_membership", None)
    exp_basket_membership_duration = basket_view_basic_data.get("exp_basket_membership_duration", None)
    exp_membership_discount = basket_view_basic_data.get("exp_membership_discount", 0)

    exp_total_activity_price = basket_view_basic_data.get("exp_total_activity_price", 0.0)
    exp_total_discounted_price = basket_view_basic_data.get("exp_total_discounted_price", 0.0)
    exp_final_price = basket_view_basic_data.get("exp_final_price", 0.0)

    exp_title = basket_view_basic_data.get("exp_title")
    exp_url = basket_view_basic_data.get("exp_url")
    exp_template_path = basket_view_basic_data.get("exp_template_path")
    exp_exist_cookies = basket_view_basic_data.get("exp_exist_cookies", [])

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

    # --------------------------------- END OF THIS TEST: test_register_get_basic --------------------------------- #


def test_basket_delete_activity_basic(app, test_client, mocker, basket_template_checker, populate_database, basket_delete_activity_basic_data):

    mocked_return_user_response = basket_delete_activity_basic_data.get("mocked_return_user_response")
    create_basket_cookie, basket_cookie_value = basket_delete_activity_basic_data.get("create_basket_cookie_and_value", (False, ""))
    create_account_cookie, account_cookie_value = basket_delete_activity_basic_data.get("create_account_cookie_and_value", (True, "Account"))

    post_dict = dict(update=basket_delete_activity_basic_data.get("update_post", False),
                     booking_id=basket_delete_activity_basic_data.get("booking_id_post", ""),
                     num_change=basket_delete_activity_basic_data.get("num_change_post", 0),
                     delete_basket=basket_delete_activity_basic_data.get("delete_basket_post", None))

    exp_status_code = basket_delete_activity_basic_data.get("exp_status_code", 200)
    exp_activities = basket_delete_activity_basic_data.get("exp_activities", [])
    exp_membership = basket_delete_activity_basic_data.get("exp_membership", None)
    exp_basket_membership_duration = basket_delete_activity_basic_data.get("exp_basket_membership_duration", None)
    exp_membership_discount = basket_delete_activity_basic_data.get("exp_membership_discount", 0)

    exp_total_activity_price = basket_delete_activity_basic_data.get("exp_total_activity_price", 0.0)
    exp_total_discounted_price = basket_delete_activity_basic_data.get("exp_total_discounted_price", 0.0)
    exp_final_price = basket_delete_activity_basic_data.get("exp_final_price", 0.0)

    exp_title = basket_delete_activity_basic_data.get("exp_title")
    exp_url = basket_delete_activity_basic_data.get("exp_url")
    exp_template_path = basket_delete_activity_basic_data.get("exp_template_path")
    exp_exist_cookies = basket_delete_activity_basic_data.get("exp_exist_cookies", [])

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

    # ----------------------------- END OF THIS TEST: test_basket_delete_activity_basic ----------------------------- #


def test_view_classes_post_basic():
    assert False
