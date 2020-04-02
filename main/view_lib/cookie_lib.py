import flask
import datetime
import hashlib

from main.data.db_classes.activity_db_class import Activity
from main.logger import log_transaction
import main.data.transactions.user_db_transaction as udf
from flask import Response
from main.data.db_classes.transaction_db_class import Receipt, Membership, MembershipType


def return_user_response(request: flask.request, needs_login: bool):
    account_id = check_valid_account_cookie(request)  # Returns user ID from cookie

    user = None
    response = None

    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            destroy_account_cookie(response)
    elif needs_login:
        response = flask.redirect('/account/login')

    return user, response


# Sets a valid account cookie consisting of the user id and a verification hash, the hash must be valid
# for the user to have access to the website on their account. This avoids users manipulating their cookie
# and gaining access to someone else's account; each cookie must have a valid hash, and that can only be
# calculated from this file
def set_auth(response: Response, user_id: int):
    hash_val = __hash_text(str(user_id))
    val = "{}:{}".format(user_id, hash_val)  # Sets the user's id as well as hash value
    response.set_cookie("vertex_account_cookie", val, max_age=datetime.timedelta(days=30))  # Sets cookie


# Destroys the user's account cookie, this is mainly utilised when the user wants to log out
def destroy_account_cookie(response: Response) -> Response:
    response.set_cookie("vertex_account_cookie", "", expires=0)  # Sets cookie to expire immediately
    return response


# Destroys the user's basket cookie, used if clearing the user's basket or if the cookie is invalid
def destroy_basket_cookie(response: Response) -> Response:
    response.set_cookie("vertex_basket_cookie", "", expires=0)  # Sets cookie to expire immediately
    return response


# Validates that the user has a valid cookie, if so, then the user can access their account
def check_valid_account_cookie(request: flask.request):
    if "vertex_account_cookie" not in request.cookies:  # Cookie does not exist
        return None

    val = request.cookies["vertex_account_cookie"]
    split_list = val.split(":")
    if len(split_list) != 2:
        log_transaction(f"IP:{request.access_route} contains invalid cookie")
        return None

    user_id = split_list[0]  # User Id is returned
    hash_val = split_list[1]  # Hash is returned
    hash_val_check = __hash_text(user_id)  # Hashed is checked to make sure the cookie is valid (ensures someone cannot
    if hash_val != hash_val_check:  # access the user account unless they have logged in successfully)
        log_transaction(f"IP:{request.access_route} has invalid cookie hash")
        return None

    try:
        user_id = int(user_id)  # Attempts to convert ID to int
    except ValueError:
        response: Response = flask.redirect("/login")  # If there is an error, then the cookie is invalid and is destroyed
        log_transaction(f"IP:{request.access_route} contains invalid cookie")
        destroy_account_cookie(response)
    else:
        return user_id # User_id is returned and the customer can successful access their account data


# Creates a sha512 hash that is used for creating secure account cookies and hashing to
# produce transaction receipts
def __hash_text(text: str) -> str:
    text = 'salty__' + text + '__text'
    return hashlib.sha512(text.encode('utf-8')).hexdigest()


# Returns cookie response
def add_activity_or_membership_to_basket(booking_object, request: flask.request, num_people=1, duration=None):

    if type(booking_object) is Activity:
        response = flask.redirect("/activities/types")
        if not num_people:
            return None
        if num_people < 1 or num_people > 8:
            return None
        add_instance = "A:" + str(booking_object.activity_id)

    elif type(booking_object) is MembershipType:
        response = flask.redirect("/info/memberships")
        if not duration:
            return None
        if duration < 1 or duration > 12:
            #out of rang
            return None
        add_instance = "M:" + str(booking_object.membership_type_id) + ":" + str(duration)
        num_people = 1

    else:
        return None

    if "vertex_basket_cookie" not in request.cookies:
        basket = add_instance
        for i in range(num_people - 1):
            basket += ";" + add_instance

        response.set_cookie("vertex_basket_cookie", basket, max_age=datetime.timedelta(days=1))
        return response

    basket = request.cookies["vertex_basket_cookie"]

    if type(booking_object) is MembershipType:
        basket_items = 0
        new_basket = ""

        for basket_instance in basket.split(";"):
            if basket_instance.split(":")[0] != "M":
                basket_items += 1
                if 1 < basket_items:
                    new_basket += ";" + basket_instance
                else:
                    new_basket = basket_instance

        if len(new_basket) is 0:
            basket = add_instance
        else:
            basket = add_instance + ";" + new_basket

    else:
        for i in range(num_people):
            basket += ";" + add_instance

    response.set_cookie("vertex_basket_cookie", basket, max_age=datetime.timedelta(days=1))
    return response


def change_items_with_id_from_cookie(id: int, num_change: int, response: flask, request: flask.request, is_activity=True):
    if "vertex_basket_cookie" not in request.cookies:
        return None

    basket = request.cookies["vertex_basket_cookie"]

    if not basket:
        return None

    basket_instances = basket.split(";")

    new_basket = ""
    num_change = int(num_change)

    for basket_instance in basket_instances:
        split_instance = basket_instance.split(":")

        if len(split_instance) not in [2, 3]:
            return None

        if not split_instance[1].isnumeric():
            return None

        if split_instance[1] == id:
            if (is_activity and split_instance[0] == "A") or (not is_activity and split_instance[0] == "M"):
                if num_change <= 0:
                    continue
                if len(new_basket) == 0:
                    new_basket = "A:" + str(id)
                else:
                    new_basket += ";A:" + str(id)
                num_change -= 1
                continue

        if len(new_basket) == 0:
            new_basket = basket_instance
        else:
            new_basket += ";" + basket_instance

    if is_activity:
        if len(new_basket) == 0 and num_change > 0:
            new_basket = "A:" + str(id)
            num_change -= 1
        for i in range(num_change):
            new_basket += ";A:" + str(id)

    response.set_cookie("vertex_basket_cookie", new_basket, max_age=datetime.timedelta(days=1))
    return response


def add_activities(added_activities, request):
    response = flask.redirect("/activities/types")
    basket_to_add = ""
    current_basket = ""

    if "vertex_basket_cookie" not in request.cookies:
        basket_to_add += "A:" + str(added_activities[0].activity_id)
        del added_activities[0]

    else:
        current_basket = request.cookies["vertex_basket_cookie"]

    for activity in added_activities:
        basket_to_add += ";" + "A:" + str(activity.activity_id)

    response.set_cookie("vertex_basket_cookie", current_basket+basket_to_add, max_age=datetime.timedelta(days=1))
    return response
