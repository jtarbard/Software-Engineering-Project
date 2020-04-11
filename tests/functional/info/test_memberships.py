import flask

from main.helper_functions.test_helpers.mocked_functions import add_to_database
from main.helper_functions.test_helpers.flask_signal_capturer import captured_templates, captured_flashes


def test_membership_view(generic_route_test, membership_view_data):
    membership_view_data["test_route"] = "/info/memberships"
    membership_view_data["database_tables"] = ["membership_type", "customer", "customer_with_membership",
                                               "membership_receipt", "membership"]

    generic_route_test("GET",
                       membership_view_data,
                       dict(standard_price=membership_view_data.get("exp_standard_price", 3),
                            premium_price=membership_view_data.get("exp_premium_price", 10),
                            standard_id=membership_view_data.get("exp_standard_id", 1),
                            premium_id=membership_view_data.get("exp_premium_id", 2)))

    # --------------------------------- END OF THIS TEST: test_membership_view --------------------------------- #


# def test_cancel_membership(app, test_client, mocker, template_checker, populate_database, cancel_membership_data):
#     mocked_return_user_response = cancel_membership_data.get("mocked_return_user_response")
#     create_basket_cookie, basket_cookie_value = cancel_membership_data.get("create_basket_cookie_and_value",
#                                                                            (False, ""))
#     create_account_cookie, account_cookie_value = cancel_membership_data.get("create_account_cookie_and_value",
#                                                                              (True, "Account"))
#
#     exp_status_code = cancel_membership_data.get("exp_status_code", 200)
#     exp_title = cancel_membership_data.get("exp_title")
#     exp_url = cancel_membership_data.get("exp_url")
#     exp_template_path = cancel_membership_data.get("exp_template_path")
#
#     exp_flash_message = cancel_membership_data.get("exp_flash_message")
#     exp_flash_category = cancel_membership_data.get("exp_flash_category")
#
#     exp_exist_cookies = cancel_membership_data.get("exp_exist_cookies", list())
#     exp_cookie_values = cancel_membership_data.get("exp_cookie_values", dict())
#
#     # ------------------------------------------------------- #
#
#     from main.helper_functions.test_helpers.database_creation import customer_with_membership_objs
#     # Get objects after database is populated (and they are created)
#     # Supply user
#     mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=mocked_return_user_response)
#     # Do not commit any database change
#     mocker.patch("main.data.db_session.add_to_database", side_effect=add_to_database)
#     # Populate database with simple dummy data
#     populate_database(["facility", "activity_type", "activity", "membership_type",
#                        "customer", "customer_with_membership", "membership_receipt", "membership"])
#
#     # ------------------------------------------------------- #
#
#     with captured_templates(app) as templates:
#         with captured_flashes(app) as flash_messages:
#
#             if create_basket_cookie:
#                 test_client.set_cookie("localhost", "vertex_basket_cookie", basket_cookie_value)
#             if create_account_cookie:
#                 test_client.set_cookie("localhost", "vertex_account_cookie", account_cookie_value)
#             rv = test_client.get("/info/memberships/cancel", follow_redirects=True)
#
#             # Check user has no membership anymore
#             user, discard1, discard2 = mocked_return_user_response(None, None)  # TODO: Investigate why discard2 returns None (although it doesn't affect the test result here)
#             if type(user) is not bool:
#                 assert user.current_membership is None
#
#             template_checker(response=rv, request=flask.request, templates=templates,
#                              flash_messages=flash_messages,
#                              exp_title=exp_title,
#                              exp_url=exp_url, exp_template_path=exp_template_path,
#                              exp_flash_message=exp_flash_message, exp_flash_category=exp_flash_category,
#                              exp_exist_cookies=exp_exist_cookies,
#                              exp_cookie_values=exp_cookie_values,
#                              exp_status_code=exp_status_code)
#
#     # ------------------------------------------------------- #
#
#     test_client.delete_cookie("localhost", "vertex_basket_cookie")
#     test_client.delete_cookie("localhost", "vertex_account_cookie")
#
#     # ---------------------------------- END OF THIS TEST: test_cancel_membership ---------------------------------- #
#
#
# def test_buy_membership(generic_get_test, buy_membership_data):
#     buy_membership_data["test_route"] = "/info/memberships"
#     buy_membership_data["database_tables"] = ["membership_type", "customer", "customer_with_membership",
#                                                "membership_receipt", "membership"]
#
#     generic_get_test(buy_membership_data, dict(exp_standard_price=membership_view_data.get("exp_standard_price", 3),
#                                                 exp_premium_price=membership_view_data.get("exp_premium_price", 10),
#                                                 exp_standard_id=membership_view_data.get("exp_standard_id", 1),
#                                                 exp_premium_id=membership_view_data.get("exp_premium_id", 2)))
#
#
#     mocked_return_user_response = buy_membership_data.get("mocked_return_user_response")
#     create_basket_cookie, basket_cookie_value = buy_membership_data.get("create_basket_cookie_and_value",
#                                                                                     (False, ""))
#     create_account_cookie, account_cookie_value = buy_membership_data.get("create_account_cookie_and_value",
#                                                                                       (True, "Account"))
#
#     post_dict = dict(buy_membership=buy_membership_data.get("buy_membership"),
#                      membership_duration=buy_membership_data.get("membership_duration"))
#
#     exp_status_code = buy_membership_data.get("exp_status_code", 200)
#     exp_title = buy_membership_data.get("exp_title")
#     exp_url = buy_membership_data.get("exp_url")
#     exp_template_path = buy_membership_data.get("exp_template_path")
#
#     exp_flash_message = buy_membership_data.get("exp_flash_message")
#     exp_flash_category = buy_membership_data.get("exp_flash_category")
#
#     exp_exist_cookies = buy_membership_data.get("exp_exist_cookies", list())
#     exp_cookie_values = buy_membership_data.get("exp_cookie_values", dict())
#
#     # ------------------------------------------------------- #
#
#     # Get objects after database is populated (and they are created)
#     # Supply user
#     mocker.patch('main.view_lib.cookie_lib.return_user_response', side_effect=mocked_return_user_response)
#     # Populate database with simple dummy data
#     populate_database(["facility", "activity_type", "activity", "membership_type", "customer"])
#
#     # ------------------------------------------------------- #
#
#     with captured_templates(app) as templates:
#         with captured_flashes(app) as flash_messages:
#
#             if create_basket_cookie:
#                 test_client.set_cookie("localhost", "vertex_basket_cookie", basket_cookie_value)
#             if create_account_cookie:
#                 test_client.set_cookie("localhost", "vertex_account_cookie", account_cookie_value)
#             rv = test_client.post("/info/memberships/buy", follow_redirects=True, data=post_dict)
#
#             template_checker(response=rv, request=flask.request, templates=templates,
#                              flash_messages=flash_messages,
#                              exp_title=exp_title,
#                              exp_url=exp_url, exp_template_path=exp_template_path,
#                              exp_flash_message=exp_flash_message, exp_flash_category=exp_flash_category,
#                              exp_exist_cookies=exp_exist_cookies,
#                              exp_cookie_values=exp_cookie_values,
#                              exp_status_code=exp_status_code)
#
#     # ------------------------------------------------------- #
#
#     test_client.delete_cookie("localhost", "vertex_basket_cookie")
#     test_client.delete_cookie("localhost", "vertex_account_cookie")
#
#     # ------------------------------------ END OF THIS TEST: test_buy_membership ------------------------------------ #
