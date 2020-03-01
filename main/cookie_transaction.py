import flask
import datetime
import hashlib
from main.logger import log_transaction
import main.data.transactions.user_db_transaction as udf
from flask import Response
from main.data.db_classes.transaction_db_class import Receipt


def return_user_response(request: flask.request, needs_login: bool):
    account_id = check_valid_account_cookie(request)  # Returns user ID from cookie

    user = None
    response = None

    if account_id:
        user = udf.return_user(account_id)  # Checks that the customer is in the database
        if not user:  # If the customer is not in the database, then that customer has been deleted, but the user
            # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            destroy_cookie(response)
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

# TODO: Add cookie name parameter
# Destroys the user's account cookie, this is mainly utilised when the user wants to log out
def destroy_cookie(response: Response):
    response.set_cookie("vertex_account_cookie", "", expires=0)  # Sets cookie to expire immediately


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
        destroy_cookie(response)
    else:
        return user_id # User_id is returned and the customer can successful access their account data


# Creates a sha512 hash that is used for creating secure account cookies and hashing to
# produce transaction receipts
def __hash_text(text: str) -> str:
    text = 'salty__' + text + '__text'
    return hashlib.sha512(text.encode('utf-8')).hexdigest()

