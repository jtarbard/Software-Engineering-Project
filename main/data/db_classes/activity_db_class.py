from datetime import datetime
from main.data.db_session import database


class ActivityType(database.Model):
    __tablename__ = 'ActivityTypes'

    activity_type_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String, nullable=False)
    description = database.Column(database.String, nullable=False)
    tags = database.Column(database.String)
    category = database.Column(database.String, nullable=False)
    minimum_age = database.Column(database.Integer, nullable=False)
    maximum_activity_capacity = database.Column(database.Integer, nullable=False)
    hourly_activity_cost = database.Column(database.Integer, nullable=False)
    hourly_activity_price = database.Column(database.Integer, nullable=False)
    valid_composite_roles = database.Column(database.String, nullable=False)
    max_staff = database.Column(database.Integer, nullable=False)
    min_staff = database.Column(database.Integer, nullable=False)

    activities = database.relationship("Activity", back_populates="activity_type")


class Activity(database.Model):
    __tablename__ = 'Activities'

    activity_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    activity_type_id = database.Column(database.Integer, database.ForeignKey("ActivityTypes.activity_type_id"), nullable=False)
    facility_id = database.Column(database.Integer, database.ForeignKey("Facilities.facility_id"), nullable=False)
    start_time = database.Column(database.DateTime, default=datetime.now, nullable=False)
    end_time = database.Column(database.DateTime, nullable=False)

    activity_type = database.relationship("ActivityType", back_populates="activities")
    employees = database.relationship("Employee_Router", back_populates="activity")
    facility = database.relationship("Facility", back_populates="activities", uselist=False)
