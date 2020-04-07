import flask

from tests.helper.flask_signal_capturer import captured_templates
from tests.helper.mocked_functions import return_logged_in_user_response, return_not_logged_in_user_response

from tests.helper.database_creation import populate_database


"""
<Rule '/account/basket' (OPTIONS, POST) -> basket.basket_delete_activity>
<Rule '/misc/add_booking_to_basket' (OPTIONS, POST) -> basket.view_classes_post>
"""


def test_basket_view_basic(app, test_client, mocker, basket_template_checker, populate_database, basket_view_basic_data):

    mocked_return_user_response, \
        (create_basket_cookie, basket_cookie_value), \
        (create_account_cookie, account_cookie_value), \
        exp_activities, exp_membership, exp_basket_membership_duration, exp_membership_discount, \
        exp_total_activity_price, exp_total_discounted_price, exp_final_price, \
        exp_title, exp_url, exp_template_path, exp_exist_cookies = basket_view_basic_data

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
                                exp_activities=exp_activities,
                                exp_membership=exp_membership,
                                exp_basket_membership_duration=exp_basket_membership_duration,
                                exp_membership_discount=exp_membership_discount,
                                exp_total_activity_price=exp_total_activity_price,
                                exp_total_discounted_price=exp_total_discounted_price,
                                exp_final_price=exp_final_price
                                )

    # ------------------------------------------------------- #

    test_client.delete_cookie("localhost", "vertex_basket_cookie")
    test_client.delete_cookie("localhost", "vertex_account_cookie")

    # --------------------------------- END OF THIS TEST: test_register_get_basic --------------------------------- #


def test_basket_delete_activity_basic():
    assert False


def test_view_classes_post_basic():
    assert False
