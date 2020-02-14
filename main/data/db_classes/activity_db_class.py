import sqlalchemy as sa
from main.data.model_base import SqlAlchemyBase
from sqlalchemy import orm
from datetime import datetime


class ActivityType(SqlAlchemyBase):
    __tablename__ = 'ActivityTypes'

    activity_type_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    tags = sa.Column(sa.String)
    category = sa.Column(sa.String, nullable=False)
    minimum_age = sa.Column(sa.Integer, nullable=False)
    maximum_activity_capacity = sa.Column(sa.Integer, nullable=False)
    hourly_activity_cost = sa.Column(sa.Integer, nullable=False)
    hourly_activity_price = sa.Column(sa.Integer, nullable=False)
    valid_composite_roles = sa.Column(sa.String, nullable=False)
    max_staff = sa.Column(sa.Integer, nullable=False)
    min_staff = sa.Column(sa.Integer, nullable=False)
    leisure_center_run = sa.Column(sa.Boolean, nullable=False)

    memberships = orm.relationship("Membership", back_populates="activity")


class Activity(SqlAlchemyBase):
    __tablename__ = 'Activities'

    activity_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    activity_type_id = sa.Column(sa.Integer, sa.ForeignKey("ActivityTypes.activity_type_id"), nullable=False)
    facility_id = sa.Column(sa.Integer, sa.ForeignKey("Facilities.facility_id"), nullable=False)
    start_time = sa.Column(sa.DateTime, default=datetime.now, nullable=False)
    end_time = sa.Column(sa.DateTime, nullable=False)

    facility = orm.relationship("Facility", back_populates="activities")
    activity_type = orm.relationship("ActivityType", back_populates="activities")