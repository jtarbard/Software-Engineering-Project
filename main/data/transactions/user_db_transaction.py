# Holds all functions related to the users of the website and the transactions with the database
import flask
import hashlib
import logging
import datetime
import main.data.db_session as db

from flask import Response
from passlib.handlers.sha2_crypt import sha512_crypt as crypto

from main.data.db_classes.transaction_db_class import Receipt
from main.data.db_classes.user_db_class import Customer, User, Employee, Manager

# Logging has been individually set for this file, as transactions in the database
# are important and must be recorded

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/transactions.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(message)s"))

logger.addHandler(file_handler)


# Hashes data passed to the function, this used for hashing user passwords
def hash_text(text: str) -> str:
    return crypto.encrypt(text, rounds=171204)


# Verifies that the hashed password from the database matches the user's plain text password input
def verify_hash(hashed_text: str, plain_text: str) -> bool:
    return crypto.verify(plain_text, hashed_text)


# Creates a sha512 hash that is used for creating secure account cookies and hashing to
# produce transaction receipts
def __hash_text(text: str) -> str:
    text = 'salty__' + text + '__text'
    return hashlib.sha512(text.encode('utf-8')).hexdigest()


# Sets a valid account cookie consisting of the user id and a verification hash, the hash must be valid
# for the user to have access to the website on their account. This avoids users manipulating their cookie
# and gaining access to someone else's account; each cookie must have a valid hash, and that can only be
# calculated from this file
def set_auth(response: Response, user_id: int):
    hash_val = __hash_text(str(user_id))
    val = "{}:{}".format(user_id, hash_val)  # Sets the user's id as well as hash value
    response.set_cookie("vertex_account_cookie", val, max_age=datetime.timedelta(days=30))  # Sets cookie


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
        logger.info(f"IP:{request.access_route} contains invalid cookie")
        return None

    user_id = split_list[0]  # User Id is returned
    hash_val = split_list[1]  # Hash is returned
    hash_val_check = __hash_text(user_id)  # Hashed is checked to make sure the cookie is valid (ensures someone cannot
    if hash_val != hash_val_check:  # access the user account unless they have logged in successfully)
        logger.info(f"IP:{request.access_route} has invalid cookie hash")
        return None

    try:
        user_id = int(user_id)  # Attempts to convert ID to int
    except ValueError:
        response: Response = flask.redirect("/login")  # If there is an error, then the cookie is invalid and is destroyed
        logger.info(f"IP:{request.access_route} contains invalid cookie")
        destroy_cookie(response)
    else:
        return user_id # User_id is returned and the customer can successful access their account data


# Utilised when creating a new customer on the database. This adds all the data entered by the user at the register page
# This function takes all the arguments for adding a new customer to the customer database. The usertype can either be:
#   - 0 : customer account
#   - 1 : employee account
#   - 2 : manager account
def create_new_user_account(title, password, first_name, last_name, email, tel_number, dob, postcode, address, country, usertype):
    session = db.create_session()
    if usertype == 0:
        new_user: Customer = Customer()
    elif usertype == 1:
        new_user: Employee = Employee()
    elif usertype == 2:
        new_user: Manager = Manager()
    else:
        return False
    new_user.first_name = first_name
    new_user.last_name = last_name.lower()
    new_user.title = title.lower()
    new_user.password = hash_text(password)
    new_user.email = email
    new_user.tel_number = tel_number
    new_user.dob = dob
    new_user.postal_code = postcode
    new_user.address = address.lower()
    new_user.country = country.lower()
    session.add(new_user)

    logger.info(f"New User {new_user.user_id} of type {type(new_user)} added")

    session.commit()

    return new_user


# Simply returns the user with matching ID. Mainly used when a user has a verified cookie and needs access to
# customer details
def return_user(account_id):
    session = db.create_session()
    returned_user: User = session.query(User).filter(User.user_id == account_id).first()
    if returned_user:
        logger.info(f"Attempting to return user: {returned_user.first_name}")
    else:
        logger.info(f"Failed to return user with ID: {account_id}")
    return returned_user


# Checks if a user of the inputted email exists and has the correct password (the user input matches
# the hashed password stored in the database)
def check_user_is_in_database_and_password_valid(email: str, password: str):
    if not email or not password:
        return None

    session = db.create_session()
    returned_user = session.query(User).filter(User.email == email).first()

    logger.info(f"Checking if:{email} has correct password")

    if not returned_user:
        logger.info(f"False: {email} does not exist")
        return False

    if not verify_hash(returned_user.password, password):  # Password does not match encrypted password
        logger.info(f"False: {email} did not enter correct password")
        return False

    session.close()
    logger.info(f"True: {email} did enter correct password")
    return returned_user


# Checks that the user has entered in a valid email by searching the database and returning
# whether an email exists or not. This is mainly used to check that the user is not registering
# with an existing email
def check_if_email_exists(email: str) -> bool:
    if not email:
        return False
    session = db.create_session()
    logger.info(f"Checking if user:{email} exists in database")
    returned_user = session.query(User).filter(User.email == email).first()  # User of that email is searched
    session.close()
    if returned_user is None:
        logger.info(f"True: {email} does not exist in database")
        return False
    else:
        logger.info(f"False: {email} does exist in database")
        return True


def return_membership_for_customer_id(customer_id: int):
    session = db.create_session()
    receipts = session.query(Receipt).filter(Receipt.customer_id == customer_id).all()
    for receipt in receipts:
        if receipt.memberships != 0:
            membership = receipt.memberships[0]
            session.close()
            return membership.membership_type_id
    return False