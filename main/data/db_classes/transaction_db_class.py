from datetime import datetime, date
from main.data.db_session import database


class Receipt(database.Model):
    __tablename__ = 'Receipts'

    receipt_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    customer_id = database.Column(database.Integer, database.ForeignKey("Customers.customer_id"), nullable=False)
    total_cost = database.Column(database.Integer, database.CheckConstraint("total_cost > 0 and total_cost < 5000"), nullable=False)
    # Total cost must be between 0 and 5000
    creation_time = database.Column(database.DateTime, default=datetime.now, nullable=False)
    # Sets the creation time to now

    # Relationships between the different trandatabasection types
    bookings = database.relationship("Booking", back_populates="receipt")
    memberships = database.relationship("Membership", back_populates="receipt")


class Booking(database.Model):
    __tablename__ = "Bookings"

    booking_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    activity_id = database.Column(database.Integer, database.ForeignKey("Activities.activity_id"), nullable=False)
    receipt_id = database.Column(database.Integer, database.ForeignKey("Receipts.receipt_id"), nullable=False)

    receipt = database.relationship("Receipt", back_populates="bookings", uselist=False)


class Membership(database.Model):
    __tablename__ = 'Memberships'

    membership_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    membership_type_id = database.Column(database.Integer, database.ForeignKey("MembershipTypes.membership_type_id"), nullable=False)
    start_date = database.Column(database.Date, default=date.today, nullable=False)
    end_date = database.Column(database.Date, default=date.today, nullable=False)
    receipt_id = database.Column(database.Integer, database.ForeignKey("Receipts.receipt_id"), nullable=False)

    receipt = database.relationship("Receipt", back_populates="memberships", uselist=False)
    membership_type = database.relationship("MembershipType", back_populates="memberships", uselist=False)


class MembershipType(database.Model):
    __tablename__ = 'MembershipTypes'

    membership_type_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String, nullable=False)
    description = database.Column(database.String, nullable=False)
    discount = database.Column(database.Integer, database.CheckConstraint("discount >= 0 and discount <= 100"), nullable=False)
    # Discount percentage must be between 0 and 100%
    monthly_price = database.Column(database.Integer, database.CheckConstraint("monthly_price >= 0"), nullable=False)

    memberships = database.relationship("Membership", back_populates="membership_type")