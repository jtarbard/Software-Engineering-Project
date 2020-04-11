

"""
Menu to all possible activity types.
"""


def test_view_activity_types_get(generic_route_test, view_activity_types_get_data):
    from main.helper_functions.test_helpers.database_creation import activity_type_objs, facility_objs

    view_activity_types_get_data["test_route"] = "/activities/types"
    view_activity_types_get_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type",
                                                       "customer", "customer_with_membership", "membership_receipt",
                                                       "membership"]

    generic_route_test(request_type="GET",
                       data=view_activity_types_get_data,
                       extra_exp_data=dict(activity_types=activity_type_objs,
                                           facilities=facility_objs))

    # ------------------------------ END OF THIS TEST: test_view_activity_types_get ------------------------------ #


def test_view_activity_types_post():
    assert False
