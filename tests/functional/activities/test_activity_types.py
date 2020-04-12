

def test_view_activity_types_get(generic_route_test, view_activity_types_get_data):
    from main.helper_functions.test_helpers.database_creation import activity_type_objs, facility_objs

    view_activity_types_get_data["test_route"] = "/activities/types"
    view_activity_types_get_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type",
                                                       "customer", "customer_with_membership", "membership_receipt",
                                                       "membership"]

    # Check all activity types are shown on the page
    exp_text = []
    for activity_type in activity_type_objs:
        exp_text.append(activity_type.name)
        exp_text.append(str(activity_type.maximum_activity_capacity))
        # exp_text.append(activity_type.tags)

    view_activity_types_get_data["exp_text"] = exp_text

    generic_route_test(request_type="GET",
                       data=view_activity_types_get_data,
                       extra_exp_data=dict(activity_types=activity_type_objs,
                                           facilities=facility_objs))

    # ------------------------------ END OF THIS TEST: test_view_activity_types_get ------------------------------ #


def test_view_activity_types_post(generic_route_test, view_activity_types_post_data):
    from main.helper_functions.test_helpers.database_creation import activity_type_objs, activity_objs

    view_activity_types_post_data["test_route"] = "/activities/types"
    view_activity_types_post_data["database_tables"] = ["facility", "activity_type", "activity", "membership_type", "customer"]

    # Check all activity type names are shown on the page
    exp_text = []
    for activity_type in activity_type_objs:
        exp_text.append(activity_type.name)

    # Check the <activity_id> row is opened
    activity_id = view_activity_types_post_data.get("activity")
    exp_text.append(activity_type_objs[activity_objs[activity_id].activity_type_id].description)

    view_activity_types_post_data["exp_text"] = exp_text

    generic_route_test(request_type="POST",
                       data=view_activity_types_post_data,
                       post_data=dict(activity=activity_id))

    # ------------------------------- END OF THIS TEST: test_view_activity_types_post ------------------------------- #
