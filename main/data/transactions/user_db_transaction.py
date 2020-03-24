# Holds all functions related to the users of the website and the transactions with the database
import main.data.db_session as db

from main.data.db_classes.user_db_class import Customer, User, Employee, Manager
from main.logger import log_transaction


# Utilised when creating a new customer on the database. This adds all the data entered by the user at the register page
# This function takes all the arguments for adding a new customer to the customer database. The usertype can either be:
#   - 0 : customer account
#   - 1 : employee account
#   - 2 : manager account
def create_new_user_account(usertype, **kwargs):
    if usertype == 0:
        new_user: Customer = Customer(**kwargs)
    elif usertype == 1:
        new_user: Employee = Employee(**kwargs)
    elif usertype == 2:
        new_user: Manager = Manager(**kwargs)
    else:
        return False

    if db.add_to_database(new_user):
        log_transaction(f"New User {new_user.user_id} of type {type(new_user)} added")
        return new_user
    else:
        print("DEBUG (udt) Failed to add new user")
        return None


# Simply returns the user with matching ID. Mainly used when a user has a verified cookie and needs access to
# customer details
def return_user(account_id):
    returned_user: User = User.query.filter(User.user_id == account_id).first()
    if returned_user is None:
        log_transaction(f"Failed to return user with ID: {account_id}")

    return returned_user


# Checks if a user of the inputted email exists and has the correct password (the user input matches
# the hashed password stored in the database)
def check_user_is_in_database_and_password_valid(email: str, password: str):
    if not email or not password:
        return None

    returned_user = User.query.filter(User.email == email).first()

    if not returned_user:
        log_transaction(f"{email} does not exist")
        return None

    if not returned_user.password_match(password):  # Password does not match encrypted password
        log_transaction(f"{email} did not enter correct password")
        return None

    return returned_user


# Checks that the user has entered in a valid email by searching the database and returning
# whether an email exists or not. This is mainly used to check that the user is not registering
# with an existing email
def check_if_email_exists(email: str) -> bool:
    if not email:
        return False

    returned_user = User.query.filter(User.email == email).first()  # User of that email is searched
    if returned_user is None:
        log_transaction(f"{email} does not exist in database")
        return False
    else:
        return True


def return_customer_with_user_id(user_id: int):
    return Customer.query.filter(Customer.user_id == user_id).first()


def return_customer_with_email(customer_email: str):
    return Customer.query.filter(Customer.email == customer_email).first()


def return_employee_with_user_id(user_id):
    return Employee.query.filter(Employee.user_id == user_id).first()