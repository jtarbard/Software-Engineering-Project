# Holds all functions related to the users of the website and the transactions with the database
import flask
import datetime
import main.helper_functions.cryptography as crypto
import main.data.transactions.activity_db_transaction as adf
import main.view_lib.basket_lib as bl
from main.logger import log_transaction
from main.data.db_session import add_to_database
from main.data.db_classes.transaction_db_class import MembershipType, Receipt, Membership
from main.data.db_classes.activity_db_class import Activity
from main.data.db_classes.transaction_db_class import Booking, PaymentDetails
from main.data.db_classes.user_db_class import User, Customer


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

    new_membership = MembershipType(name=name, description=description, discount=discount, monthly_price=monthly_price)

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
    print(flask.request.cookies)
    if "vertex_basket_cookie" not in request.cookies:
        return True, None, None, None

    basket = request.cookies["vertex_basket_cookie"]

    if not basket:
        return False, None, None, None

    basket_instances = basket.split(";")

    basket_activities = []
    basket_membership = None
    basket_membership_duration = None

    # basket_instances = A:10;A:10;A:10
    # A:10;M:1:3;A:10
    for basket_instance in basket_instances:
        split_instance = basket_instance.split(":")

        if len(split_instance) not in [2, 3]:
            return False, None, None, None

        if not split_instance[1].isnumeric():
            return False, None, None, None

        if split_instance[0] == "M":
            new_membership = return_membership_type_with_id(split_instance[1])
            # TODO: Comment (Only allow 1 membership; if multiple encountered then return false)
            if basket_membership or not new_membership:
                return False, None, None, None

            basket_membership = new_membership
            basket_membership_duration = int(split_instance[2])

        elif split_instance[0] == "A":
            new_activity: Activity = adf.return_activity_with_id(split_instance[1])
            # TODO: Add more validation (e.g. date validation)
            if not new_activity:
                return False, None, None, None

            basket_activities.append(new_activity)

        else:
            return False, None, None, None

    return True, basket_activities, basket_membership, basket_membership_duration


def return_bookings_with_activity_id(activity_id):
    return Booking.query.filter(Booking.activity_id == activity_id, Booking.deleted == False).all()


def create_new_receipt(basket_activities, basket_membership: MembershipType, user: User, membership_duration: int):
    customer = Customer.query.filter(Customer.user_id == user.user_id).first()
    new_receipt = Receipt(customer_id=customer.customer_id, total_cost=0, creation_time=datetime.datetime.now())
    add_to_database(new_receipt)

    total_price = 0

    regular_discounts = bl.return_regular_discounts(basket_activities)

    for i, activity in enumerate(basket_activities):
        new_booking = Booking(activity_id=activity.activity_id, receipt_id=new_receipt.receipt_id)
        duration: datetime.timedelta = activity.end_time - activity.start_time
        current_price = (duration.seconds // 3600 * activity.activity_type.hourly_activity_price)

        total_price += current_price - (current_price * regular_discounts[i] / 100)
        add_to_database(new_booking)

    if basket_membership:
        total_price -= total_price * basket_membership.discount/100

        total_price += basket_membership.monthly_price * membership_duration

        new_membership = Membership(membership_type_id=basket_membership.membership_type_id,
                                    start_date=datetime.date.today(),
                                    end_date=datetime.date.today() + datetime.timedelta(days=30*membership_duration),
                                    receipt_id=new_receipt.receipt_id)

        new_membership.membership_type = basket_membership

        add_to_database(new_membership)

        customer = Customer.query.filter_by(user_id=user.user_id).first()
        customer.current_membership_id = new_membership.membership_id
        add_to_database(customer)

    new_receipt.total_cost = round(total_price, 2)
    add_to_database(new_receipt)

    return new_receipt.receipt_id


def check_encrypted_receipt(encrypted_receipt: str, user: User):
    customer = Customer.query.filter(Customer.user_id == user.user_id).first()
    receipts = Receipt.query.filter(Receipt.customer_id == customer.customer_id).all()

    for receipt in receipts:
        plain_text = str(receipt.receipt_id) + "-" + str(user.user_id)
        if crypto.verify_hash(encrypted_receipt, plain_text):
            return receipt

    return False


def return_receipt_with_id(receipt_id):
    return Receipt.query.filter(Receipt.receipt_id == receipt_id).first()


def set_deletion_for_receipt_bookings_with_activity(receipt, activity):
    booking_to_delete = Booking.query.filter_by(receipt_id=receipt.receipt_id, activity_id=activity.activity_id).all()

    if not booking_to_delete:
        return False

    for booking in booking_to_delete:
        booking.deleted = True
        add_to_database(booking)

    return True


# [Lewis S]
# Adds a customers card details to the database as well as connecting to the customer table for an key relationship
def add_new_card_details(customer_obj: Customer, **card_details_kwargs):

    payment_detail = PaymentDetails(**card_details_kwargs)

    add_to_database(payment_detail)

    customer_obj.payment_detail = payment_detail
    add_to_database(customer_obj)

    return True
