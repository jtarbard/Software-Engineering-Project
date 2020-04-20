import re
import datetime

import main.data.transactions.user_db_transaction as udf
from main.data.db_classes.user_db_class import Customer


def get_membership_type(user):
    membership = None
    if user.__mapper_args__['polymorphic_identity'] == "Customer":
        customer: Customer = udf.return_customer_with_user_id(user.user_id)

        if customer.current_membership is not None:
            membership = customer.current_membership.membership_type

    return membership


def validate_user_details(**kwargs):
    title = kwargs.get("title", None)
    password_first = kwargs.get('password_first', None)
    password_second = kwargs.get('password_second', None)
    first_name = kwargs.get('first_name', None)
    last_name = kwargs.get('last_name', None)
    email = kwargs.get('email', None)
    check_email = kwargs.get("check_email", False)
    tel_number = kwargs.get('tel_number', None)
    dob = kwargs.get('dob', None)
    postcode = kwargs.get('postcode', None)
    address = kwargs.get('address', None)
    country = kwargs.get('country', None)
    current_date = kwargs.get('current_date', None)

    server_error = None

    # For all of the main string values that the user enters, the fields are checked to make sure they are
    # Valid, this is done using the check_if_input_error() function in the user transactions
    fields_to_check = [password_first, first_name, last_name, tel_number, postcode, address]
    for field in fields_to_check:
        if field is not None:
            special_character_regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
            if special_character_regex.search(field) or len(field) < 3 or len(field) > 40:
                server_error = "Input error: " + field + " is not a valid input"
                break

    if title is not None and len(title) > 5:  # Checks the title is greater than 5
        server_error = "Input Error: Title is not valid"
    elif password_first is not None and (len(password_first) < 8 or len(password_first) > 15):  # Checks password size
        server_error = "Input error: password is not of correct size (8-15)"
    elif address is not None and (len(address) < 10 or len(address) > 40):
        server_error = "Input error: address is not of correct size (10-40)"  # Checks address is valid
    elif ( first_name is not None and (len(first_name) < 3 or len(first_name) > 15) ) or ( last_name is not None and (len(last_name) < 3 or len(last_name) > 15) ):  # Checks first and last name sizes
        server_error = "Input error: first name or last name of incorrect length"
    elif title is not None and (len(tel_number) > 11 or len(tel_number) < 7):  # Checks telephone number length
        server_error = "Input error: telephone of incorrect length"
    elif title is not None and (len(country) > 5 or len(country) < 2):  # Checks country code length
        server_error = "Input error: country of incorrect length"

    formatted_dob = None
    if dob is not None:
        if type(dob) == datetime.datetime:
            dob = str(dob.date())
        date_values = dob.split("-")
        formatted_dob = datetime.date(int(date_values[0]), int(date_values[1]), int(date_values[2]))
    if email is not None and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):  # Validates email format
        server_error = "Input Error: Email not in valid format"
    elif postcode is not None and not re.fullmatch(  # Validates postcode based on the regex provided by the Government
            r"([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})",
            postcode):
        server_error = "Input Error: Post code not in valid format"
    elif first_name is not None and not first_name.isalpha():  # First name can only be alphabets
        server_error = "Input Error: First name can only contain english alphabets"
    elif last_name is not None and not last_name.isalpha():  # Last name can only be alphabets
        server_error = "Input Error: Last name can only contain english alphabets"
    elif tel_number is not None and not tel_number.isnumeric():  # Telephone can only contain numbers
        server_error = "Input Error: telephone not in valid format"
    elif check_email and email is not None and udf.check_if_email_exists(email):  # Checks if email exists in database
        server_error = "Input Error: Email already exists"
    elif password_first is not None and password_second is not None and password_first != password_second:  # Checks that both passwords match
        server_error = "Input Error: Passwords do not match"
    elif password_first is not None and " " in password_first:  # Makes sure password doesn't contain spaces
        server_error = "Input Error: Password cannot contain spaces"
    elif password_first is not None and not any(num in password_first for num in
                 ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]):  # Checks password has a number
        server_error = "Input Error: Password must contain a number"
    elif dob is not None and current_date is not None and formatted_dob > current_date - datetime.timedelta(
            days=365 * 16 + 4):  # Checks that user is over 16 (takes account into leap years)
        server_error = "Input Error: Incorrect date of birth entered (must be over 16)"

    return server_error is None, server_error
