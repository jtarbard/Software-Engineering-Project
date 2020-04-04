import re
import flask
import datetime
import random
import string

import main.data.transactions.user_db_transaction as udf
import main.data.transactions.activity_db_transaction as adf
import main.view_lib.cookie_lib as cl
from main.data.db_classes.activity_db_class import ActivityType
from main.data.db_classes.user_db_class import Customer, Manager, Employee
from main.data.transactions.transaction_db_transaction import add_new_card_details
from main.view_lib import account_lib
import main.data.db_session as ds

blueprint = flask.Blueprint("account", __name__)


# Route for executing when the customer clicks a link to the login page
@blueprint.route("/account/login", methods=["GET"])
def login_get():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if user:
        return flask.redirect("/")

    if "vertex_basket_cookie" in flask.request.cookies:
        response = flask.redirect("/account/login")
        response.set_cookie("vertex_basket_cookie", "", expires=0)
        return response

    return flask.render_template("/account/login_register.html", page_type="login", has_cookie=has_cookie)


# Route for executing when the customer submits login data from the login page
@blueprint.route("/account/login", methods=["POST"])
def login_post():
    data_form = flask.request
    password_first = data_form.form.get('password') # Retrieves posted password
    email = data_form.form.get('email') # Retrieves posted email
    server_error = None

    # This validation works by initially having the server error be None, if the server error is set to a value other
    # Then the None value, then an error must have occurred and the user cannot log in

    special_character_regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

    if len(password_first) < 8 or len(password_first) > 15: # Checks password size is between 8 and 15
        server_error = "Input error: password is not of correct size (8-15)"

    elif special_character_regex.search(password_first):
        server_error = "Input Error: Password not in valid format"

    if server_error:  # Returns login page if an error is found
        return flask.render_template("account/login_register.html", page_type="login", ServerError=server_error,
                                     email=email, has_cookie=True, page_title="Login")

    # Checks that the customer exists in the database, if not then the login page returned with an error
    user = udf.check_user_is_in_database_and_password_valid(email, password_first)
    if not user:  # Checks if the user actually exists
        return flask.render_template("account/login_register.html", page_type="login",
                                     ServerError="Input error: Incorrect email or password",
                                     email=email, has_cookie=True, page_title="Login")

    # Implies that no error has occurred and the user is redirected to their account. A cookie is then set that
    # Verifies the customer ID and a verification hash
    response = flask.redirect('/account/home')
    cl.set_auth(response, user.user_id)  # Creates user cookie
    return response


# Route for executing when the customer clicks a link to the register page
@blueprint.route("/account/register", methods=["GET"])
def register_get():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if user:
        return flask.redirect("/")

    if "vertex_basket_cookie" in flask.request.cookies:
        response = flask.redirect("/account/register")
        response.set_cookie("vertex_basket_cookie", "", expires=0)
        return response


    return flask.render_template("/account/login_register.html", page_type="register", has_cookie=has_cookie)


# Route for executing when the customer submits register data from the register page
@blueprint.route("/account/register", methods=["POST"])
def register_post():

    server_error = None
    # All of the values the user entered at the register page
    data_form = flask.request
    title = data_form.form.get("title")
    password_first = data_form.form.get('password_first')
    password_second = data_form.form.get('password_second')
    first_name = data_form.form.get('first_name')
    last_name = data_form.form.get('last_name')
    email = data_form.form.get('email')
    tel_number = data_form.form.get('tel_number')
    dob = data_form.form.get('dob')
    postcode = data_form.form.get('postcode')
    address = data_form.form.get('address')
    country = data_form.form.get('country')
    current_date = datetime.date.today()

    # For all of the main string values that the user enters, the fields are checked to make sure they are
    # Valid, this is done using the check_if_input_error() function in the user transactions
    fields_to_check = [password_first, first_name, last_name, tel_number, postcode, address]
    for field in fields_to_check:

        special_character_regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if special_character_regex.search(field) or len(field) < 3 or len(field) > 40:
            server_error = "Input error: " + field + " is not a valid input"
            break

    if len(title) > 5: # Checks the title is greater than 5
        server_error = "Input Error: Title is not valid"
    elif len(password_first) < 8 or len(password_first) > 15: # Checks password size
        server_error = "Input error: password is not of correct size (8-15)"
    elif len(address) < 10 or len(address) > 40:
        server_error = "Input error: address is not of correct size (10-40)" # Checks address is valid
    elif len(first_name) < 3 or len(first_name) > 15 or len(last_name) < 3 or len(last_name) > 15: # Checks first and last name sizes
        server_error = "Input error: first name or last name of incorrect length"
    elif len(tel_number) > 11 or len(tel_number) < 7: # Checks telephone number length
        server_error = "Input error: telephone of incorrect length"
    elif len(country) > 5 or len(country) < 2: # Checks country code length
        server_error = "Input error: country of incorrect length"

    date_values = dob.split("-")
    formatted_dob = datetime.date(int(date_values[0]), int(date_values[1]), int(date_values[2]))
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):  # Validates email format
        server_error = "Input Error: Email not in valid format"
    elif not re.fullmatch( # Validates postcode based on the regex provided by the Government
            r"([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})",
            postcode):
        server_error = "Input Error: Post code not in valid format"
    elif not tel_number.isnumeric(): # Telephone can only contain numbers
        server_error = "Input Error: telephone not in valid format"
    elif udf.check_if_email_exists(email):  # Checks if email exists in database
        server_error = "Input Error: Email already exists"
    elif password_first != password_second:  # Checks that both passwords match
        server_error = "Input Error: Passwords do not match"
    elif " " in password_first: # Makes sure password doesn't contain spaces
        server_error = "Input Error: Password cannot contain spaces"
    elif not any(num in password_first for num in ["0","1","2","3","4","5","6","7","8","9"]): # Checks password has a number
        server_error = "Input Error: Password must contain a number"
    elif formatted_dob > current_date - datetime.timedelta(days=365 * 16):  # Checks that user is over 16
        server_error = "Input Error: Incorrect date of birth entered (must be over 16)"

    if server_error:  # If there was an error then the normal register page is loaded with all the values that the user
                      # entered inserted into the fields

        return flask.render_template("account/login_register.html", page_type="register",
                                     ServerError=server_error, email=email, date_of_birth=str(dob), first_name=first_name,
                                     last_name=last_name, postcode=postcode, address=address, title=title,
                                     tel_number=tel_number, page_title="Register")

    # user is created and returned
    user = udf.create_new_user_account(0, title=title, password=password_first, first_name=first_name, last_name=last_name,
                                       email=email, tel_number=tel_number, dob=formatted_dob, postal_code=postcode,
                                       address=address, country=country)

    # Account cookie is checked
    response = flask.redirect('/account/home')
    cl.set_auth(response, user.user_id)  # Creates user cookie
    return response


# Route for executing if the user clicks to view their account
@blueprint.route("/account/home", methods=["GET"])
def view_account():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    membership_type = account_lib.get_membership_type(user)

    return flask.render_template("/account/account_home.html", User=user, membership_type=membership_type, page_title="Your Account", sidebar_off=True)


@blueprint.route("/account/receipts", methods=["GET"])
def view_account_receipts(returned_receipts=None):
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    if user.__mapper_args__['polymorphic_identity'] == "Customer":
        customer: Customer = udf.return_customer_with_user_id(user.user_id)
        returned_receipts = customer.purchases
    elif user.__mapper_args__['polymorphic_identity'] == "Employee":
        employee: Employee = udf.return_employee_with_user_id(user.user_id)
        returned_receipts = employee.receipt_assist
    elif user.__mapper_args__['polymorphic_identity'] == "Manager":
    #     TODO: add manager functionality: returning all receipts between certain dates.
        returned_receipts = []
    else:
        return flask.abort(500)

    returned_receipts.reverse() #reverse so that items appear in chronological order

    membership_type = account_lib.get_membership_type(user)

    return flask.render_template("/account/receipts.html", User=user, has_cookie=has_cookie,
                                 returned_receipts=returned_receipts, membership_type=membership_type, page_title="Receipts")

# def get_start_time(elem):
#         return elem[2]


@blueprint.route("/account/bookings", methods=["GET"])
def view_account_bookings():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    returned_bookings = {}
    if user.__mapper_args__['polymorphic_identity'] == "Customer":
        if user.__mapper_args__['polymorphic_identity'] == "Customer":
            customer: Customer = udf.return_customer_with_user_id(user.user_id)
            for receipt in customer.purchases:
                for booking in receipt.bookings:
                    if booking.activity.start_time > datetime.datetime.now() and booking.deleted == False:
                        if booking.activity not in returned_bookings:
                            returned_bookings[booking.activity] = [receipt, 1, booking.activity.start_time]
                        else:
                            returned_bookings[booking.activity][1] += 1
    elif user.__mapper_args__['polymorphic_identity'] == "Employee":
        returned_bookings = {}
    elif user.__mapper_args__['polymorphic_identity'] == "Manager":
    #     TODO: add manager functionality: returning booking stats.
        returned_bookings = {}
    else:
        return flask.abort(500)

    membership_type = account_lib.get_membership_type(user)

    return flask.render_template("/account/bookings.html", User=user,
                                 returned_bookings=returned_bookings, membership_type=membership_type,
                                 page_title="Upcoming Bookings", has_cookie=has_cookie)


@blueprint.route("/account/membership", methods=["GET"])
def view_account_membership():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    customer: Customer = udf.return_customer_with_user_id(user.user_id)

    membership = None
    for receipt in customer.purchases:
        if receipt.membership:
            membership = receipt.membership
            break

    membership_type = account_lib.get_membership_type(user)

    return flask.render_template("/account/membership.html", User=user,
                                 membership_type=membership_type, membership=membership, page_title="Membership", has_cookie=has_cookie)

@blueprint.route("/account/details", methods=["GET", "POST"])
def view_account_details():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    customer: Customer = udf.return_customer_with_user_id(user.user_id)
    membership_type = account_lib.get_membership_type(user)

    if flask.request.method == "POST":
        data_form = flask.request.form


        #TODO: create input validation function to remove repeated code
        server_error = None
        # All of the values the user entered at the register page
        details = {
            "first_name": data_form.get("first_name"),
            "last_name": data_form.get("last_name"),
            "title": data_form.get("title"),
            "email": data_form.get("email"),
            "dob": datetime.datetime.strptime(data_form.get("dob"), "%Y-%m-%d"),
            "tel_number": data_form.get("tel_number"),
            "country": data_form.get("country"),
            "postal_code": data_form.get("postal_code"),
            "address": data_form.get("address"),
        }

        if server_error is not None:
            flask.flash(server_error, "error")
        else:
            udf.edit_user_account(customer.user_id, details)

    return flask.render_template("/account/account_details.html", User=user, customer=customer, membership_type=membership_type, page_title="Account Details", has_cookie=has_cookie)


@blueprint.route("/account/card", methods=["POST", "GET"])
def view_payment_details():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    customer: Customer = udf.return_customer_with_user_id(user.user_id)
    membership_type = account_lib.get_membership_type(user)

    if customer.payment_detail:
        payment_details = vars(customer.payment_detail)
    else:
        payment_details = None

    print(payment_details)

    if flask.request.method == "POST":
        data_form = flask.request.form

        if payment_details is not None:
            ds.delete_from_database(customer.payment_detail)

        if data_form.get("delete") == "True":
            print("VALUE IS TRUE")
            ds.delete_from_database(customer.payment_detail)
        else:
            add_new_card_details(customer, card_number=data_form.get('card_number'),
                                     start_date=data_form.get('start_date'),
                                     expiration_date=data_form.get('expiration_date'),
                                     street_and_number=data_form.get('street_and_number'),
                                     town=data_form.get('town'), city=data_form.get('city'),
                                     postcode=data_form.get('postcode'))

        if customer.payment_detail:
            payment_details = vars(customer.payment_detail)
        else:
            payment_details = None

    return flask.render_template("/account/card_details.html", User=user, customer=customer, payment_details=payment_details, membership_type=membership_type, page_title="Card Details", has_cookie=has_cookie)

@blueprint.route("/account/view_statistics", methods=["POST", "GET"])
def view_usages():
    user, response, has_cookie = cl.return_user_response(flask.request, True)
    if response:
        return response

    if type(user) != Manager:
        return flask.redirect("/account/your_account")

    data_form = flask.request.form

    start_date = data_form.get("start_date")
    end_date = data_form.get("end_date")

    fixed_cost = 11500  # fixed cost per week the sports centre needs to pay for (For realism)

    if type(start_date) is str:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    if type(end_date) is str:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    activity_type_id = data_form.get("activity_type_id")

    if not start_date:
        start_date = datetime.date.today() - datetime.timedelta(hours=24*7)
    if not end_date:
        end_date = datetime.date.today()

    if not activity_type_id:
        activity_type_id = "Any"
    elif activity_type_id != "Any":
        activity_type_id = int(activity_type_id)

    start_search = datetime.datetime.combine(start_date, datetime.datetime.min.time())
    end_search = datetime.datetime.combine(end_date, datetime.datetime.min.time())

    activities = adf.return_activity_instances_between_dates(activity_type_id, end_search, start_search)

    activity_types = adf.return_all_activity_types()

    if not activities:
        weekly_activities = None
        total_activity_type_bookings = None
    else:
        weekly_activities = {}
        total_activity_type_bookings = {}

        for activity_type in activity_types:
            color = ""
            for i in range(6):
                color += random.choice("abcdef" + string.digits)
            total_activity_type_bookings[activity_type] = [0, color]

    total_cash_in = 0
    total_cash_out = 0
    total_bookings = 0

    start_date_monday = start_search - datetime.timedelta(days=start_search.weekday())
    end_date_monday = end_search - datetime.timedelta(days=end_search.weekday())

    number_of_weeks = (end_date_monday-start_date_monday).days // 7

    for activity in activities:
        activity_type: ActivityType = activity.activity_type
        num_activity_bookings = len(activity.bookings)

        activity_income = num_activity_bookings * activity_type.hourly_activity_price * (activity.end_time - activity.start_time).seconds//3600
        activity_cost = num_activity_bookings * activity_type.hourly_activity_cost * (activity.end_time - activity.start_time).seconds//3600
        activity_week = ((activity.end_time - datetime.timedelta(days=activity.end_time.weekday()))-start_date_monday).days // 7

        if activity_week not in weekly_activities:
            weekly_activities[activity_week] = {}

        if activity_type not in weekly_activities[activity_week]:
            weekly_activities[activity_week][activity_type] = [[activity, activity_income, activity_cost, num_activity_bookings]]
        else:
            weekly_activities[activity_week][activity_type].append([activity, activity_income, activity_cost, num_activity_bookings])

        if "income" not in weekly_activities[activity_week]:
            weekly_activities[activity_week]["income"] = activity_income
        else:
            weekly_activities[activity_week]["income"] += activity_income

        if "cost" not in weekly_activities[activity_week]:
            weekly_activities[activity_week]["cost"] = activity_cost
        else:
            weekly_activities[activity_week]["cost"] += activity_cost

        if "num_bookings" not in weekly_activities[activity_week]:
            weekly_activities[activity_week]["num_bookings"] = num_activity_bookings
        else:
            weekly_activities[activity_week]["num_bookings"] += num_activity_bookings

        if "color" not in weekly_activities[activity_week]:
            color = ""
            for i in range(6):
                color += random.choice("abcdef" + string.digits)
            weekly_activities[activity_week]["color"] = color

        total_cash_in += activity_income
        total_cash_out += activity_cost
        total_bookings += num_activity_bookings
        total_activity_type_bookings[activity_type][0] += num_activity_bookings

    total_activity_type_bookings = {k: v for k, v in sorted(total_activity_type_bookings.items(), key=lambda item: item[1][0], reverse=True)}
    activity_types = list(total_activity_type_bookings.keys())

    for week_num in weekly_activities.keys():
        weekly_activities[week_num]["cost"] += fixed_cost
        total_cash_out += fixed_cost

    search_field_data = {}
    search_field_data["start_date"] = start_date.strftime("%Y-%m-%d")
    search_field_data["end_date"] = end_date.strftime("%Y-%m-%d")
    search_field_data["max_date"] = datetime.date.today()
    search_field_data["activity_type"] = activity_type_id

    return flask.render_template("/account/statistics.html", User=user, number_of_weeks=number_of_weeks+1,
                                 weekly_activities=weekly_activities, search_field_data=search_field_data,
                                 activity_types=activity_types, total_cash_in=total_cash_in,
                                 total_cash_out=total_cash_out, total_bookings=total_bookings,
                                 total_activity_type_bookings=total_activity_type_bookings, page_title="Statistics",
                                 has_cookie=has_cookie)


# Route for executing if the user wants to log out
@blueprint.route("/account/log_out")
def log_out():
    response = flask.redirect("/")
    cl.destroy_account_cookie(response)  # User cookie is destroyed and they are logged out
    if "vertex_basket_cookie" in flask.request.cookies:
        response.set_cookie("vertex_basket_cookie", "", expires=0)
    return response
