from datetime import datetime
from main.data.db_session import database

from main.helper_functions.cryptography import hash_text, verify_hash


# Class mapped to the user table in the database, this is the parent class to the: customer, employee and
# manager classes; this is defined by the __mapper_args__ field
class User(database.Model):
    __tablename__ = 'Users'

    user_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    first_name = database.Column(database.String, nullable=False)
    last_name = database.Column(database.String, nullable=False)
    title = database.Column(database.String)
    email = database.Column(database.String, nullable=False, index=True)
    password = database.Column(database.String, nullable=False, index=True)
    dob = database.Column(database.Date)
    tel_number = database.Column(database.String)
    country = database.Column(database.String)
    postal_code = database.Column(database.String)
    address = database.Column(database.String)
    creation_date = database.Column(database.DateTime, default=datetime.now)

    discriminator = database.Column('type', database.String(50)) #Type of user
    __mapper_args__ = {
        'polymorphic_on': discriminator
    }

    def __init__(self, first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address, creation_date=None):
        self.first_name = first_name
        self.last_name = last_name.lower()
        self.title = title.lower()
        self.email = email
        self.password = hash_text(password)
        self.dob = dob
        self.tel_number = tel_number
        self.country = country.lower()
        self.postal_code = postal_code
        self.address = address.lower()
        if creation_date is not None:
            self.creation_date = creation_date

    def password_match(self, plain_text_password) -> bool:
        return verify_hash(self.password, plain_text_password)


# Employee class that maps to the user table, data is automatically added to the user table when referencing the
# employee, manager and customer tables
class Employee(User):
    __tablename__ = 'Employees'

    employee_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    user_id = database.Column(database.Integer, database.ForeignKey("Users.user_id"), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Employee'
    }

    router_activities = database.relation("Employee_Router", backref="employee")
    # invisible virtual attribute "allowed_roles" for many-to-many relationship
    # invisible virtual attribute "receipt_assist" for many-to-many relationship

    def __init__(self, first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address, creation_date=None):
        super().__init__(first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address, creation_date)


class Customer(User):
    __tablename__ = 'Customers'

    customer_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    user_id = database.Column(database.Integer, database.ForeignKey("Users.user_id"), nullable=False)
    current_membership_id = database.Column(database.Integer, database.ForeignKey("Memberships.membership_id"))

    __mapper_args__ = {
        'polymorphic_identity': 'Customer'
    }

    current_membership = database.relation("Membership")
    purchases = database.relation("Receipt", backref="customer")
    payment_detail = database.relation("PaymentDetails", backref="customer", uselist=False, lazy=True)

    def __init__(self, first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address, creation_date=None):
        super().__init__(first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address, creation_date)


class Manager(User):
    __tablename__ = 'Managers'

    manager_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    user_id = database.Column(database.Integer, database.ForeignKey("Users.user_id"), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Manager'
    }

    def __init__(self, first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address, creation_date=None):
        super().__init__(first_name, last_name, title, email, password, dob, tel_number, country, postal_code, address, creation_date)


class PaymentDetails(database.Model):
    __tablename__ = 'PaymentDetails'

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    card_number = database.Column(database.String)
    start_date = database.Column(database.String)
    expiration_date = database.Column(database.String)

    street_and_number = database.Column(database.String)
    town = database.Column(database.String)
    city = database.Column(database.String)
    postcode = database.Column(database.String)

    customer_id = database.Column(database.Integer, database.ForeignKey('Customers.customer_id'))
    #imaginary field "customer"
