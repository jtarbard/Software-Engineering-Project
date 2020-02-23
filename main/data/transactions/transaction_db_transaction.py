# Holds all functions related to the users of the website and the transactions with the database
import flask
import hashlib
import logging
import datetime
import main.data.db_session as db

from flask import Response
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from main.data.db_classes.transaction_db_class import Booking, Receipt, MembershipType, Membership

# Logging has been individually set for this file, as transactions in the database
# are important and must be recorded

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/transactions.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(message)s"))

logger.addHandler(file_handler)


#  A simple function that returns a list of all the membership types currently in the gym
def return_all_membership_types():
    session = db.create_session()
    return session.query(MembershipType).all()


#  Creates a new membership type, only if the following conditions are met:
#     -Name is between lengths 4 and 20 and is not numeric
#     -Description is between lengths 10 and 200 and is not numeric
#     -Discount is a valid percentage (between 0-100)
#     -Monthly_price is between £0 and £100
#     -Membership name does not already exist in the database
def create_new_membership_type(name: str, description: str, discount: int, monthly_price: float):
    if len(name) < 4 or len(name) > 20 or not name.replace(" ", "").isalpha():
        logger.info(f"Failed to add new membership {name}: name not correct length or type")
        return False
    if len(description) < 10 or len(description) > 200:
        logger.info(f"Failed to add new membership {name}: description not correct length or type")
        return False
    if discount < 0 or discount > 100:
        logger.info(f"Failed to add new membership {name}: invalid discount value")
        return False
    if monthly_price < 0 or monthly_price > 100:
        logger.info(f"Failed to add new membership {name}: invalid monthly_price value")
        return False

    membership_types = return_all_membership_types()
    for membership in membership_types:
        if membership.name == name.lower():
            logger.info(f"Failed to add new membership {name}: membership name already exists")
            return False

    session = db.create_session()
    new_membership = MembershipType()
    new_membership.name = name.lower()
    new_membership.description = description.lower()
    new_membership.discount = discount
    new_membership.monthly_price = monthly_price

    logger.info(f"Adding new membership {name}")
    session.add(new_membership)
    session.commit()
    session.close()
    return True


