from datetime import datetime
from main.data.db_session import database


# Many to many relationship
activity_available_at = \
    database.Table("ActivityAvailableAt",
                   database.Column('session_type_id', database.Integer,
                                   database.ForeignKey('SessionTypes.session_type_id')),
                   database.Column('facility_id', database.Integer,
                                   database.ForeignKey('Facilities.facility_id'))
                   )

activity_roles = \
    database.Table("valid_activity_roles_association",
        database.Column("role_id", database.Integer, database.ForeignKey("Roles.role_id")),
        database.Column("session_type_id", database.Integer, database.ForeignKey("SessionTypes.session_type_id"))
)


class ActivityType(database.Model):
    __tablename__ = 'ActivityTypes'

    activity_type_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String, nullable=False)

    session_types = database.relationship("SessionType", back_populates="activity_type")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # .lower() to avoid duplicates of different cases
        self.name = kwargs.get("name", "UNKNOWN_ACTIVITY_TYPE").lower()


class SessionType(database.Model):
    __tablename__ = 'SessionTypes'

    session_type_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    activity_type_id = database.Column(database.Integer, database.ForeignKey("ActivityTypes.activity_type_id"),
                                       nullable=False)
    session_type_name = database.Column(database.String, nullable=False)
    description = database.Column(database.Text, nullable=False)
    tags = database.Column(database.String)
    category = database.Column(database.String, nullable=False)
    minimum_age = database.Column(database.Integer, nullable=False)
    maximum_activity_capacity = database.Column(database.Integer, nullable=False)
    hourly_activity_cost = database.Column(database.Integer, nullable=False)
    hourly_activity_price = database.Column(database.Integer, nullable=False)
    max_staff = database.Column(database.Integer, nullable=False)
    min_staff = database.Column(database.Integer, nullable=False)

    activity_type = database.relationship("ActivityType", back_populates="session_types")
    activities = database.relationship("Activity", back_populates="session_type")
    available_facilities = \
        database.relationship("Facility",
                              secondary=activity_available_at,
                              backref=database.backref('activities_available', lazy='dynamic'))

    # invisible virtual attribute "allowed_roles" for many-to-many relationship

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # .lower() to avoid duplicates of different cases
        self.session_type_name = kwargs.get("session_type_name", "UNKNOWN_SESSION_TYPE").lower()


class Activity(database.Model):
    __tablename__ = 'Activities'

    activity_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    session_type_id = database.Column(database.Integer, database.ForeignKey("SessionTypes.session_type_id"),
                                      nullable=False)
    activity_type_id = database.Column(database.Integer, database.ForeignKey("ActivityTypes.activity_type_id"),
                                       nullable=False)
    facility_id = database.Column(database.Integer, database.ForeignKey("Facilities.facility_id"), nullable=False)
    start_time = database.Column(database.DateTime, default=datetime.now, nullable=False)
    end_time = database.Column(database.DateTime, nullable=False)

    session_type = database.relationship("SessionType", back_populates="activities")

    employees = database.relationship("Employee_Router", back_populates="activity")
    facility = database.relationship("Facility", back_populates="current_activities", uselist=False)
    bookings = database.relationship("Booking", back_populates="activity")


class FacilityType(database.Model):
    """
    FacilityType contains the items that will show up in the Facilities page on the website.
    """

    __tablename__ = 'FacilityTypes'

    facility_type_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    facility_type_name = database.Column(database.String, nullable=False)
    description = database.Column(database.Text, nullable=False)
    max_capacity = database.Column(database.Integer, nullable=False)

    facilities = database.relationship("Facility", back_populates="facility_type")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # .lower() to avoid duplicates of different cases
        self.facility_type_name = kwargs.get("facility_type_name", "UNKNOWN_FACILITY_TYPE_NAME").lower()


class Facility(database.Model):
    """
    Facility contains individual facility objects.
    This allows for multiple facilities of the same "type", for example, Sports Hall 1 and Sports Hall 2.
    """

    __tablename__ = "Facilities"

    facility_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    facility_type_id = database.Column(database.Integer, database.ForeignKey("FacilityTypes.facility_type_id"),
                                       nullable=False)
    name = database.Column(database.String, nullable=False)  # calling this name as before for backwards compactibility

    facility_type = database.relationship("FacilityType", back_populates="facilities")
    current_activities = database.relationship("Activity", back_populates="facility")

    # invisible backref list parameter from ActivityType : activities_available
    # e.g. Facility.query.first().activities_available

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # .lower() to avoid duplicates of different cases
        self.name = kwargs.get("name", "UNKNOWN_FACILITY_NAME").lower()
