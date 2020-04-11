

def test_facilities_view(generic_route_test, facilities_view_data):
    facilities_view_data["test_route"] = "/info/facilities"
    facilities_view_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type",
                                               "customer", "customer_with_membership", "membership_receipt",
                                               "membership"]

    generic_route_test(request_type="GET",
                       data=facilities_view_data)
