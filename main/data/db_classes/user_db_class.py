import sqlalchemy as sa
from sqlalchemy import orm
from datetime import datetime
from main.data.model_base import SqlAlchemyBase

# Class mapped to the user table in the database, this is the parent class to the: customer, employee and
# manager classes; this is defined by the __mapper_args__ field
class User(SqlAlchemyBase):
    __tablename__ = 'Users'

    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String)
    email = sa.Column(sa.String, nullable=False, index=True)
    password = sa.Column(sa.String, nullable=False, index=True)
    dob = sa.Column(sa.Date)
    tel_number = sa.Column(sa.String)
    country = sa.Column(sa.String)
    postal_code = sa.Column(sa.String)
    address = sa.Column(sa.String)
    creation_date = sa.Column(sa.DateTime, default=datetime.now)

    discriminator = sa.Column('type', sa.String(50)) #Type of user
    __mapper_args__ = {
        'polymorphic_on': discriminator
    }


# Employee class that maps to the user table, data is automatically added to the user table when referencing the
# employee, manager and customer tables
class Employee(User):
    __tablename__ = 'Employees'

    employee_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("Users.user_id"), nullable=False)
    composite_roles = sa.Column(sa.String, nullable=False) # Integer related to the roles that a user is allowed
                                                           # To partake in for certain activities

    __mapper_args__ = {
        'polymorphic_identity': 'Employee'
    }

    router_activities = orm.relation("Employee_Router", backref="employee")


class Customer(User):
    __tablename__ = 'Customers'

    customer_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("Users.user_id"), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Customer'
    }

    purchases = orm.relation("Receipt", backref="customer")


class Manager(User):
    __tablename__ = 'Managers'

    manager_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("Users.user_id"), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Manager'
    }

