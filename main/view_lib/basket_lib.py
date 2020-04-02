import main.data.transactions.activity_db_transaction as adf


def return_activity_type_count_from_activity_list(basket_activities):
    activity_type_count = [0 for activity in adf.return_all_activity_types()]
    for activity in list(dict.fromkeys(basket_activities)):
        activity_type_count[activity.activity_type_id-1] += 1
    return activity_type_count


def return_bulk_discount(activity, activity_type_count=None, basket_activities=None):
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