import pytest
import flask

from main.data.transactions.transaction_db_transaction import return_activities_and_memberships_from_basket_cookie_if_exists

from tests.helper.database_creation import populate_database


def test_return_activities_and_memberships_from_basket_cookie_if_exists(test_client, populate_database, basket_cookie_data):
    """
    Test for checking whether the basket cookie can be decoded correctly.
    :param cookie_value: basket cookie value
    :param exp_output: a 4-tuple (1, 2, 3, 4)
    :param test_client: fixture
    :param basket_cookies_db: setup database (once per function) for basket cookie tests
    1. Boolean: true if cookie decoded properly and booking returned correctly; false otherwise
    2. List of activity objects which have ids that are stored in the cookie
    3. Singular membership object which have id stored in the cookie
    4. Duration (in months) of the membership object which is stored in the cookie
    """

    populate_database(["facility", "membership_type", "activity_type", "activity"])

    # ------------------------------------------------------- #

    cookie_value, exp_output = basket_cookie_data
    print("Cookie:\t\t", cookie_value)

    test_client.set_cookie("localhost", "vertex_basket_cookie", cookie_value)
    test_client.get("/")
    var1, var2, var3, var4 = return_activities_and_memberships_from_basket_cookie_if_exists(flask.request)
    exp1, exp2, exp3, exp4 = exp_output
    print("Expected:\t", exp1, exp2, exp3, exp4)
    print("Got:\t\t", var1, var2, var3, var4)
    assert var1 == exp1, "Expected true if cookie decoded properly and booking returned correctly; false otherwise"
    assert var2 == exp2, "Expected List of activity objects which have ids that are stored in the cookie"
    assert var3 == exp3, "Expected Singular membership object which have id stored in the cookie"
    assert var4 == exp4, "Expected Duration (in months) of the membership object which is stored in the cookie"
