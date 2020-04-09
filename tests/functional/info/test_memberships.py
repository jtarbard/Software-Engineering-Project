import flask

from main.helper_functions.test_helpers.flask_signal_capturer import captured_templates


def test_membership_view(app, test_client, mocker, memberships_template_checker, populate_database, membership_view_data):
    mocked_return_user_response = membership_view_data.get("mocked_return_user_response")
    create_basket_cookie, basket_cookie_value = membership_view_data.get("create_basket_cookie_and_value",
                                                                         (False, ""))
    create_account_cookie, account_cookie_value = membership_view_data.get("create_account_cookie_and_value",
                                                                           (False, ""))

    exp_status_code = membership_view_data.get("exp_status_code", 200)
    exp_title = membership_view_data.get("exp_title")
    exp_url = membership_view_data.get("exp_url")
    exp_template_path = membership_view_data.get("exp_template_path")
    exp_exist_cookies = membership_view_data.get("exp_exist_cookies", [])

    exp_standard_price = membership_view_data.get("exp_standard_price", 3)
    exp_premium_price = membership_view_data.get("exp_premium_price", 10)
    exp_standard_id = membership_view_data.get("exp_standard_id", 1)
    exp_premium_id = membership_view_data.get("exp_premium_id", 2)

    # ------------------------------------------------------- #

    # Get objects after database is populated (and they are created)
    mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=mocked_return_user_response)
    # Populate database with simple dummy data
    populate_database(["membership_type",
                       "customer", "customer_with_membership", "membership_receipt", "membership"])

    # ------------------------------------------------------- #

    with captured_templates(app) as templates:

        if create_basket_cookie:
            test_client.set_cookie("localhost", "vertex_basket_cookie", basket_cookie_value)
        if create_account_cookie:
            test_client.set_cookie("localhost", "vertex_account_cookie", account_cookie_value)
        rv = test_client.get("/info/memberships", follow_redirects=True)

        memberships_template_checker(response=rv, request=flask.request, templates=templates, exp_title=exp_title,
                                     exp_url=exp_url, exp_template_path=exp_template_path,
                                     exp_exist_cookies=exp_exist_cookies,
                                     exp_status_code=exp_status_code,
                                     exp_standard_price=exp_standard_price, exp_premium_price=exp_premium_price,
                                     exp_standard_id=exp_standard_id, exp_premium_id=exp_premium_id)

    # ------------------------------------------------------- #

    test_client.delete_cookie("localhost", "vertex_basket_cookie")
    test_client.delete_cookie("localhost", "vertex_account_cookie")

    # --------------------------------- END OF THIS TEST: test_membership_view --------------------------------- #


def test_cancel_membership():
    """
    <Rule '/info/memberships/cancel' (OPTIONS, HEAD, GET) -> info.cancel_membership>
    """
    assert False


def test_buy_membership():
    """
    <Rule '/info/memberships/buy' (OPTIONS, POST) -> info.buy_membership>
    """
    assert False
