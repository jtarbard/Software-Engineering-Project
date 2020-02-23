import re
import flask
import datetime
import main.data.transactions.user_db_transaction as udf

blueprint = flask.Blueprint("account", __name__)


# Route for executing when the customer clicks a link to the login page
@blueprint.route("/account/login", methods=["GET"])
def login_get():
    account_id = udf.check_valid_account_cookie(flask.request) # Checks if the user is already logged in
    if account_id: # If an account cookie and ID is found then the customer is checked to
                   # see if they are in the database
        customer = udf.return_user(account_id)
        if customer: # If customer is in the database then the customer is taken to the index page, as they
                     # should not have access to the login/ register page if they are logged in
            return flask.redirect("/") # Returns the customer to the index page if they are already logged in

    # Normal login page is loaded if the customer is not logged in
    return flask.render_template("/account/login_register.html", nav=True, footer=True, page_type="login")


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
                                     email=email, has_cookie=True, nav=True, footer=True)

    # Checks that the customer exists in the database, if not then the login page returned with an error
    user = udf.check_user_is_in_database_and_password_valid(email, password_first)
    if not user:  # Checks if the user actually exists
        return flask.render_template("account/login_register.html", page_type="login",
                                     ServerError="Input error: Incorrect email or password",
                                     email=email, has_cookie=True, nav=True, footer=True)

    # Implies that no error has occurred and the user is redirected to their account. A cookie is then set that
    # Verifies the customer ID and a verification hash
    response = flask.redirect('/account/your_account')
    udf.set_auth(response, user.user_id)  # Creates user cookie
    return response


# Route for executing when the customer clicks a link to the register page
@blueprint.route("/account/register", methods=["GET"])
def register_get():
    account_id = udf.check_valid_account_cookie(flask.request)
    if account_id:
        customer = udf.return_user(account_id)
        if customer:
            return flask.redirect("/") # Returns user to home page if they are logged in

    return flask.render_template("/account/login_register.html", nav=True, footer=True, page_type="register")


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
    elif not any(num in password_first for num in ["1","2","3","4","5","6","7","8","9"]): # Checks password has a number
        server_error = "Input Error: Password must contain a number"
    elif formatted_dob > current_date - datetime.timedelta(days=365 * 16):  # Checks that user is over 16
        server_error = "Input Error: Incorrect date of birth entered (must be over 16)"

    if server_error: # If there was an error then the normal register page is loaded with all the values that the user
                     # entered inserted into the fields

        return flask.render_template("account/login_register.html", page_type="register",
                                     ServerError=server_error, email=email, date_of_birth=str(dob), first_name=first_name,
                                     last_name=last_name, postcode=postcode, address=address, title=title,
                                     tel_number=tel_number, nav=True, footer=True)

    # user is created and returned
    user = udf.create_new_user_account(title, password_first, first_name, last_name, email, tel_number, formatted_dob,
                                  postcode, address, country, 0)

    # Account cookie is checked
    response = flask.redirect('/account/your_account')
    udf.set_auth(response, user.user_id)  # Creates user cookie
    return response


# Route for executing if the user clicks to view their account
@blueprint.route("/account/your_account")
def view_account():
    account_id = udf.check_valid_account_cookie(flask.request) # Returns user ID from cookie
    if account_id:
        user = udf.return_user(account_id) # Checks that the customer is in the database
        if not user: # If the customer is not in the database, then that customer has been deleted, but the user
                         # still has an account cookie, therefore the cookie must be destroyed as it is no longer valid
            response = flask.redirect('/account/login')
            udf.destroy_cookie(response)
            return response
    else:
        return flask.redirect('/account/login') # If the use does not have an account cookie then they are taken to the
                                                # login page

    return flask.render_template("/account/your_account.html", nav=True, footer=True, User=user, User_Type=user.__mapper_args__["polymorphic_identity"])


# Route for executing if the user wants to log out
@blueprint.route("/account/log_out")
def log_out():
    response = flask.redirect("/")
    udf.destroy_cookie(response)  # User cookie is destroyed and they are logged out
    return response
