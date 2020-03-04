from datetime import datetime
from main.data.db_session import database


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

class Customer(User):
    __tablename__ = 'Customers'

    customer_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    user_id = database.Column(database.Integer, database.ForeignKey("Users.user_id"), nullable=False)
    current_membership = database.Column(database.Integer, database.ForeignKey("Memberships.membership_id"))

    __mapper_args__ = {
        'polymorphic_identity': 'Customer'
    }

    purchases = database.relation("Receipt", backref="customer")


class Manager(User):
    __tablename__ = 'Managers'

    manager_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    user_id = database.Column(database.Integer, database.ForeignKey("Users.user_id"), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Manager'
    }
