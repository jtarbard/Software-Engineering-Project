import sqlalchemy as sa
from sqlalchemy import orm
from datetime import datetime
from main.data.model_base import SqlAlchemyBase

#Customer_Connection = sa.Table(
#    "Customer_Connection",
#    SqlAlchemyBase.metadata,
#    sa.Column("connection_id", sa.Integer, primary_key=True, autoincrement=True),
#    sa.Column("customer_primary_id", sa.Integer, sa.ForeignKey("Customer.customer_id")),
#    sa.Column("customer_secondary_id",sa.Integer, sa.ForeignKey("Customer.customer_id")),
#    sa.Column("pending", sa.Boolean, default=True),
#    sa.Column("date_created", sa.Date, default=datetime.now()),
#)


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
    user_type = sa.Column(sa.Integer, sa.CheckConstraint("user_type >= 0 and user_type <= 2"), default=0)

    discriminator = sa.Column('type', sa.String(50))
    __mapper_args__ = {
        'polymorphic_on': discriminator
    }


class Employee(User):
    __tablename__ = 'Employees'

    employee_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("Users.user_id"), nullable=False)
    composite_roles = sa.Column(sa.String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Employee'
    }

    activities = orm.relation("Employee_Router", backref="employees")


class Customer(User):
    __tablename__ = 'Customers'

    customer_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("Users.user_id"), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Customer'
    }

    purchases = orm.relation("Receipt", backref="customer")
    #friends = orm.relation("Customer", secondary="Customer_Connection",
    #                       primaryjoin=(id == Customer_Connection.c.customer_primary_id),
    #                       secondaryjoin=id == Customer_Connection.c.customer_secondary_id)


class Manager(User):
    __tablename__ = 'Managers'

    manager_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("Users.user_id"), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Manager'
    }

