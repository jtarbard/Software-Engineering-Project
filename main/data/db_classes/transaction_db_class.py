from datetime import datetime, date
import sqlalchemy as sa
from main.data.model_base import SqlAlchemyBase
from sqlalchemy import orm


class Receipt(SqlAlchemyBase):
    __tablename__ = 'Receipts'

    receipt_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    customer_id = sa.Column(sa.Integer, sa.ForeignKey("Customers.customer_id"), nullable=False)
    total_cost = sa.Column(sa.Integer, sa.CheckConstraint("total_cost > 0 and total_cost < 5000"), nullable=False)
    # Total cost must be between 0 and 5000
    creation_time = sa.Column(sa.DateTime, default=datetime.now, nullable=False)
    # Sets the creation time to now

    # Relationships between the different transaction types
    bookings = orm.relationship("Booking", back_populates="receipt")
    memberships = orm.relationship("Membership", back_populates="receipt")


class Booking(SqlAlchemyBase):
    __tablename__ = "Bookings"

    booking_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    activity_id = sa.Column(sa.Integer, sa.ForeignKey("Activities.activity_id"), nullable=False)
    receipt_id = sa.Column(sa.Integer, sa.ForeignKey("Receipts.receipt_id"), nullable=False)

    receipt = orm.relationship("Receipt", back_populates="bookings", uselist=False)


class Membership(SqlAlchemyBase):
    __tablename__ = 'Memberships'

    membership_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    membership_type_id = sa.Column(sa.Integer, sa.ForeignKey("MembershipTypes.membership_type_id"), nullable=False)
    start_date = sa.Column(sa.Date, default=date.today, nullable=False)
    end_date = sa.Column(sa.Date, default=date.today, nullable=False)
    receipt_id = sa.Column(sa.Integer, sa.ForeignKey("Receipts.receipt_id"), nullable=False)

    receipt = orm.relationship("Receipt", back_populates="memberships", uselist=False)
    membership_type = orm.relationship("MembershipType", back_populates="memberships", uselist=False)


class MembershipType(SqlAlchemyBase):
    __tablename__ = 'MembershipTypes'

    membership_type_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    discount = sa.Column(sa.Integer, sa.CheckConstraint("discount >= 0 and discount <= 100"), nullable=False)
    # Discount percentage must be between 0 and 100%
    monthly_price = sa.Column(sa.Integer, sa.CheckConstraint("monthly_price >= 0"), nullable=False)

    memberships = orm.relationship("Membership", back_populates="membership_type")
