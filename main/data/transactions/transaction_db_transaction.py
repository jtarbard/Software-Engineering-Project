# Holds all functions related to the users of the website and the transactions with the database
import flask
import hashlib
import logging
import datetime
from main.data.db_session import session, add_to_database
from main.logger import log_transaction

from flask import Response
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from main.data.db_classes.transaction_db_class import Booking, Receipt, MembershipType, Membership


#  A simple function that returns a list of all the membership types currently in the gym
def return_all_membership_types():
    return session.query(MembershipType).all()


#  Creates a new membership type, only if the following conditions are met:
#     -Name is between lengths 4 and 20 and is not numeric
#     -Description is between lengths 10 and 200 and is not numeric
#     -Discount is a valid percentage (between 0-100)
#     -Monthly_price is between £0 and £100
#     -Membership name does not already exist in the database
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

    return add_to_database(new_membership)
