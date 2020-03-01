# Holds all functions related to the users of the website and the transactions with the database
import flask
from main.data.db_session import session, add_to_database
from main.logger import log_transaction
from main.data.db_classes.transaction_db_class import MembershipType
from main.data.db_classes.activity_db_class import Activity
import main.data.transactions.activity_db_transaction as adf
from main.data.db_classes.transaction_db_class import Booking

#  A simple function that returns a list of all the membership types currently in the gym
def return_all_membership_types():
    return MembershipType.query.all()


#  Creates a new membership type, only if the following conditions are met:
#     -Name is between lengths 4 and 20 and is not numeric
#     -Description is between lengths 10 and 200 and is not numeric
#     -Discount is a valid percentage (between 0-100)
#     -Monthly_price is between £0 and £100
#     -Membership name does not already exist in the database
# [Lewis S]
def create_new_membership_type(name: str, description: str, discount: int, monthly_price: float):
    if len(name) < 4 or len(name) > 20 or not name.replace(" ", "").isalpha():
        log_transaction(f"Failed to add new membership {name}: name not correct length or type")
        return False
    if len(description) < 10 or len(description) > 200:
        log_transaction(f"Failed to add new membership {name}: description not correct length or type")
        return False
    if discount < 0 or discount > 100:
        log_transaction(f"Failed to add new membership {name}: invalid discount value")
        return False
    if monthly_price < 0 or monthly_price > 100:
        log_transaction(f"Failed to add new membership {name}: invalid monthly_price value")
        return False

    membership_types = return_all_membership_types()
    for membership in membership_types:
        if membership.name == name.lower():
            log_transaction(f"Failed to add new membership {name}: membership name already exists")
            return False

    new_membership = MembershipType()
    new_membership.name = name.lower()
    new_membership.description = description.lower()
    new_membership.discount = discount
    new_membership.monthly_price = monthly_price

    log_transaction(f"Adding new membership {name}")
    return add_to_database(new_membership)


# Simply returns the membership with a specific ID
# [Lewis S]
def return_membership_type_with_id(id: int):
    membership : MembershipType = MembershipType.query.filter(MembershipType.membership_type_id == id).first()
    if not membership:
        log_transaction(f"Failed to return membership with ID {id}: does not exist in database")
    else:
        log_transaction(f"Successfully returned membership with ID {id}")
    return membership


# Attempts to return all activity or membership instances stored in the basket cookie. These are stored in a specific
# format:
#   - Each item in the basket is split into a list, being separated by a semi-colon
#   - An item consists of two parts:
#       - The type of item in the basket (membership/activity)
#       - The ID of the item stored in the database
# Thus each of the items is extracted and used for extracting the correct activities and memberships from the cookie.
# The function will however return false, if the following conditions are met:
#   - A cookie is found but cannot be extracted
#   - An item instance does not consist of the two parts (type and ID)
#   - The ID is not numeric
#   - An activity item does not return a valid activity
#   - A membership item does not return a valid membership
#   - The type is not formatted to be a membership or activity
#  Returns values:
#   - Boolean: true if cookie decoded properly and booking returned correctly; false otherwise
#   - List of activity objects which have ids that are stored in the cookie
#   - List of membership objects which have ids that are stored in the cookie
# [Lewis S]
def return_activities_and_memberships_from_basket_cookie_if_exists(request: flask.request):
    # TODO: Comment
    if "vertex_basket_cookie" not in request.cookies:
        return True, None, None

    basket = request.cookies["vertex_basket_cookie"]

    if not basket:
        return False, None, None

    basket_instances = basket.split(";")

    basket_activities = []
    basket_membership = None

    for basket_instance in basket_instances:
        split_instance = basket_instance.split(":")

        if len(split_instance) != 2:
            return False, None, None

        if not split_instance[1].isnumeric():
            return False, None, None

        if split_instance[0] == "M":
            new_membership = return_membership_type_with_id(split_instance[1])
            # TODO: Comment (Only allow 1 membership; if multiple encountered then return false)
            if basket_membership or not new_membership:
                return False, None, None

            basket_membership = new_membership

        elif split_instance[0] == "A":
            new_activity: Activity = adf.return_activity_with_id(split_instance[1])
            # TODO: Add more validation (e.g. date validation)
            if not new_activity:
                return False, None, None

            basket_activities.append(new_activity)

        else:
            return False, None, None

    return True, basket_activities, basket_membership

"""
def add_items_and_membership_to_basket(request: flask.request, response: flask.Response, membership: MembershipType, activity: Activity):

    if activity:
        add_instance = "A:" + str(activity.activity_id)
    elif membership:
        add_instance = "M" + str(membership.membership_type_id)
    else:
        return False, request

    if "vertex_basket_cookie" not in request.cookies:
        response.set_cookie("vertex_basket_cookie", add_instance, max_age=datetime.timedelta(days=1))
        return True, response

    basket = request.cookies["vertex_basket_cookie"]
    basket += ";".encode("utf-8") + add_instance

    response.set_cookie("vertex_basket_cookie", "", max_age=0)
    return True, response
"""


def return_bookings_with_activity_id(activity_id):
    return Booking.query.filter(Booking.activity_id == activity_id).all()
