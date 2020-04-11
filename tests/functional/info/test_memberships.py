import flask


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


def test_cancel_membership(generic_route_test, cancel_membership_data):
    cancel_membership_data["test_route"] = "/info/memberships/cancel"
    cancel_membership_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type",
                                                 "customer", "customer_with_membership", "membership_receipt",
                                                 "membership"]

    generic_route_test(request_type="GET",
                       data=cancel_membership_data)

    # ------------------------------------------------------- #

    mocked_return_user_response = cancel_membership_data.get("mocked_return_user_response")

    # ------------------------------------------------------- #

    # Check user has no membership anymore
    user, discard1, discard2 = mocked_return_user_response(None, None)  # TODO: Investigate why discard2 returns None (although it doesn't affect the test result here)
    if type(user) is not bool:
        assert user.current_membership is None

    # ---------------------------------- END OF THIS TEST: test_cancel_membership ---------------------------------- #


def test_buy_membership(generic_route_test, buy_membership_data):
    buy_membership_data["test_route"] = "/info/memberships/buy"
    buy_membership_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type", "customer"]

    generic_route_test(request_type="POST",
                       data=buy_membership_data,
                       post_data=dict(buy_membership=buy_membership_data.get("buy_membership"),
                                      membership_duration=buy_membership_data.get("membership_duration")))

    # ------------------------------------ END OF THIS TEST: test_buy_membership ------------------------------------ #
