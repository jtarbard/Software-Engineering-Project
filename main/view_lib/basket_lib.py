import main.data.transactions.activity_db_transaction as adf


def return_activity_type_count_from_activity_list(basket_activities):
    activity_type_count = [0 for activity in adf.return_all_activity_types()]
    for activity in list(dict.fromkeys(basket_activities)):
        activity_type_count[activity.activity_type_id-1] += 1
    return activity_type_count


def return_bulk_discount(activity, activity_type_count=None, basket_activities=None):
    """
    Deprecated. Use return_regular_discounts instead
    """
    if not basket_activities and not activity_type_count:
        return False

    if not activity_type_count and basket_activities:
        activity_type_count = return_activity_type_count_from_activity_list(basket_activities)

    num_activity_type = activity_type_count[activity.activity_type_id-1]
    if num_activity_type >= 10:
        bulk_discount = 0.5
    elif num_activity_type >= 5:
        bulk_discount = 0.3
    elif num_activity_type >= 3:
        bulk_discount = 0.15
    else:
        bulk_discount = 0

    return bulk_discount


def return_regular_discounts(basket_activities=None):
    """
    Returns a list of integers from 0 to 100 representing the percentage of discount to be applied to each activity in basket_activities.
    For example, basket_activities = [activity_4, activity_8] --- return [0, 15] means apply 0% off to activity_4 and 15% off to activity_8.

    :param basket_activities: a list of activity objects
    """

    def regular_discount(item_count):
        if item_count >= 10:
            return 50
        elif item_count >= 5:
            return 30
        elif item_count >= 3:
            return 15
        return 0

    # Using the activity_id of the first returned regular activity list as the key,
    # increment if the same list is returned
    activity_regular_key = list()
    prev_activity_id = -1  # used to check if the current activity id is the same as the previous one
    regular_count = dict()

    for activity in basket_activities:
        first_act_id = adf.return_regular_activities_before(activity_obj=activity)[0].activity_id
        activity_regular_key.append(first_act_id)

        if regular_count.get(first_act_id, None) is None:
            regular_count[first_act_id] = 1
        # If the basket contains multiple bookings of the same activity, only count the activity once
        elif not activity.activity_id == prev_activity_id:
            regular_count[first_act_id] += 1

        prev_activity_id = activity.activity_id

    print(activity_regular_key)
    print(regular_count)
    return [regular_discount(regular_count[key]) for key in activity_regular_key]
