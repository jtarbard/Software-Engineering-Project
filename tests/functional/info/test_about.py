

def test_about_get(generic_route_test, about_get_data):
    """
    GIVEN a Flask application
    WHEN the '/info/about' page is requested (GET)
    THEN check the response is valid

    TESTING FOR <Rule '/info/about' (OPTIONS, HEAD, GET) -> info.about_view>
    """

    about_get_data["test_route"] = "/info/about"
    about_get_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type",
                                         "customer", "customer_with_membership", "membership_receipt",
                                         "membership"]

    generic_route_test(request_type="GET",
                       data=about_get_data)
