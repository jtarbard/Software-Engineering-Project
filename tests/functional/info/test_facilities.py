

def test_facilities_view(generic_route_test, facilities_view_data):
    from main.helper_functions.test_helpers.database_creation import facility_objs

    facilities_view_data["test_route"] = "/info/facilities"
    facilities_view_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type",
                                               "customer", "customer_with_membership", "membership_receipt",
                                               "membership"]

    # Check all facilities are shown on the page
    exp_text = []
    for facility in facility_objs:
        exp_text.append(facility.name)
        exp_text.append(facility.description)
        exp_text.append(str(facility.max_capacity))

    facilities_view_data["exp_text"] = exp_text

    generic_route_test(request_type="GET",
                       data=facilities_view_data)
