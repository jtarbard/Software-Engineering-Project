# Holds all functions related to the activities of the website and the transactions with the database
import datetime
import csv
from main.data.db_session import add_to_database
from main.logger import log_transaction

from main.data.db_classes.activity_db_class import ActivityType, SessionType, Activity, FacilityType, Facility
import main.data.transactions.employee_data_transaction as edf

TAGS_CSV = "main/data/transactions/valid_tags.csv"


def return_facility_types():
    """
    Returns all facility types as a list
    """
    return FacilityType.query.all()


def return_facility_type_with_name(name: str):
    """
    Returns the facility type with the same name as the parameter
    """
    return FacilityType.query.filter(FacilityType.facility_type_name == name.lower()).first()


def return_session_type_with_id(session_type_id: int):
    """
    Returns the SessionType with the same id as the parameter
    [Lewis S]
    """
    return SessionType.query.filter(SessionType.session_type_id == session_type_id).first()


# Attempts to return the name of an session type with a specific activity ID, this is to combat
# lazy loading errors
# [Lewis S]
def return_session_type_name_with_activity_id(activity_id):
    activity_obj = return_activity_with_id(activity_id)
    if activity_obj is None:
        return "MissingActivity"

    # if not activity_type:
    #     log_transaction(f"Failed to return activity type name with activity type ID: {activity_type_id} from DB")
    # else:
    #     log_transaction(f"Successfully returned activity type name with activity type ID: {activity_type_id} from DB")

    return str(activity_obj.session_type.session_type_name)


# Returns the session type with the same name as the parameter
# [Lewis S]
def return_session_type_with_name(session_type_name: str):
    return SessionType.query.filter(SessionType.session_type_name == session_type_name.lower()).first()


# Attempts to add a tag to the list of tags in the csv file, if the tag exists in the csv file then the new tag is
# not added, otherwise the tag is appended to the end of the file
# [Lewis S]
def add_tag(tag: str):
    all_tags = return_valid_tags_from_file()
    if tag.lower() in all_tags:
        return False
    with open(TAGS_CSV, "a", newline="") as tag_file:
        tag_writer = csv.writer(tag_file, delimiter=",")
        tag_writer.write(tag)
    return True


# Attempts to remove a tag from the tag_list file, if found then the tag parameter is removed from the file. If
# the tag is not found in the file of tags then the False is returned
# [Lewis S]
def remove_tag(tag: str):
    all_tags = return_valid_tags_from_file()
    try:
        all_tags.remove(tag.lower())
    except ValueError:
        return False
    with open(TAGS_CSV, "w+", newline="") as tag_file:
        tag_write = csv.writer(tag_file, delimiter=",")
        tag_write.seek(0)
        tag_write.truncate()
        tag_write.write(all_tags)
    return True


# Returns all the tags from the valid_tags.csv file
def return_valid_tags_from_file():
    all_tags = []
    with open(TAGS_CSV, newline="") as tag_file:
        tag_reader = csv.reader(tag_file)
        for line in tag_reader:
            all_tags += line
    return all_tags


# Checks that the tag is stored in the list of avaliable tags
def check_tags_are_valid(tag_list: list):
    valid_tags = return_valid_tags_from_file()
    for tag in tag_list:
        if tag.lower() not in [x.lower() for x in valid_tags]:
            return False
    return True


def return_all_activity_types():
    """
    Returns all the activity types (e.g. "Tennis") stored in the database
    """
    return ActivityType.query.all()


def return_all_session_types():
    """
    Returns all the session types (e.g. "Tennis Team Event") stored in the database
    """
    return SessionType.query.all()


# Used for creating a new session type, each of the following parameters are checked as follows:
#    -Name must been 3 and 20, and cannot contain spaces or special characters, and the activity of that
#     name cannot already be in the database
#    -Description must be between 10 and 200
#    -Minimum age must be between 0 and 100
#    -Maximum capacity must be less than or equal to 150 (as the largest facility has the the maximum
#     capacity of 150)
#    -Hourly activity cost must be between 0 and 200
#    -Hourly activity price must be between 0 and 50
#    -Valid composite rules are checked to match the roles stored in the database
#    -Max staff must be between 0 and 15
#    -Min staff must be between 0 and 10 (and minimum staff must be less than the maximum staff)
#    -The tags must match the tags stored in the valid_tags.csv file
# [Lewis S]
def create_new_session_type(activity_type_name: str, name: str, description: str, category: str, tags_list: list,
                            minimum_age: int, maximum_activity_capacity: int,
                            hourly_activity_cost: int, hourly_activity_price: int,
                            max_staff: int, min_staff: int):

    activity_type = return_activity_type_with_name(activity_type_name)

    if activity_type is None:
        log_transaction(f"Failed to add new session type {name}: did not find an activity type with name {activity_type_name}")
        return False
    if len(name) < 3 or len(name) > 20 or not name.replace(" ", "").isalpha():
        log_transaction(f"Failed to add new session type {name}: name not correct length or type")
        return False
    if len(category) < 4 or len(category) > 20 or not category.replace(" ", "").isalpha():
        log_transaction(f"Failed to add new session type {name}: category not correct length or type")
        return False
    if len(description) < 10 or len(description) > 400:
        log_transaction(f"Failed to add new session type {name}: description not correct length or type")
        return False
    if minimum_age < 0 or minimum_age > 100:
        log_transaction(f"Failed to add new session type {name}: maximum_age or miniumum_age not correct size")
        return False
    if maximum_activity_capacity > 150:
        log_transaction(f"Failed to add new session type {name}: maximum_activity_capacity not correct size")
        return False
    if hourly_activity_cost < 0 or hourly_activity_price < 0 or hourly_activity_price > 50 or hourly_activity_cost > 200:
        log_transaction(f"Failed to add new session type {name}: hourly cost or price not correct size")
        return False
    if max_staff > 15 or max_staff < 0 or min_staff < 0 or min_staff > 10:
        log_transaction(f"Failed to add new session type {name}: max_staff or min_staff not correct size")
        return False

    if not check_tags_are_valid(tags_list):
        log_transaction(f"Failed to add new session type {name}: invalid tag instance")
        return False

    tags = ":".join(tags_list)
    if len(tags) > 200:
        log_transaction(f"Failed to add new session type {name}: tag length too long")
        return False

    session_types = return_all_session_types()
    for session_type in session_types:
        if session_type.session_type_name == name.lower():
            log_transaction(f"Failed to add new session type {name}: session type name already exists")
            return False

    new_session_type = SessionType(activity_type_id=activity_type.activity_type_id,
                                   session_type_name=name, description=description,
                                   category=category, tags=tags, minimum_age=minimum_age,
                                   maximum_activity_capacity=maximum_activity_capacity,
                                   hourly_activity_cost=hourly_activity_cost,
                                   hourly_activity_price=hourly_activity_price,
                                   max_staff=max_staff, min_staff=min_staff)

    add_to_database(new_session_type)
    return True


#  Takes two datetime variables and searches the activity table for a given activity ID that is between the two datetimes.
#  This function will return false if:
#       - The activity type is not an integer, or "Any"
#       - The start and end datetimes are more than 6 hours apart, or are less than an hour apart
#       - The activity type for the given ID could not be returned
#  If these are valid then the table is searched and a list of activity istances are returned
# [Lewis S]
def return_activity_instances_between_dates(session_type_id, start_time: datetime.datetime, end_time: datetime.datetime):
    start_time = start_time.replace(second=0, microsecond=0, minute=0, hour=start_time.hour) + datetime.timedelta(hours=start_time.minute // 30)
    end_time = end_time.replace(second=0, microsecond=0, minute=0, hour=end_time.hour) + datetime.timedelta(hours=end_time.minute // 30)

    if session_type_id == "Any":
        return Activity.query.filter(Activity.start_time <= start_time, Activity.end_time >= end_time).all()

    if type(session_type_id) is not int:
        log_transaction(
            f"Failed to return session type with id {session_type_id} starting on {start_time}: facility id or activity type id invalid")
        return False
    if end_time > start_time + datetime.timedelta(hours=6) or end_time < start_time + datetime.timedelta(hours=1):
        log_transaction(
            f"Failed to return session type with id {session_type_id} starting on {start_time}: date times invalid")
        return False
    if not return_session_type_with_id(session_type_id):
        log_transaction(
            f"Failed to return session type with id {session_type_id} starting on {start_time}: activity type does not exist")
        return False

    return Activity.query.filter(Activity.session_type_id == session_type_id,
                                 Activity.start_time <= start_time,
                                 Activity.end_time >= end_time).all()


# Used for creating a new activity instance, this takes an activity type, facility id, start and end datetimes.
# The function will fail if the following occur:
#       - The activity type is not an integer
#       - The activity duration is larger than 6 hours or smaller than 1 hour
#       - The activity starts before 6:00am or ends after 10:00pm
#       - The facility name does not return a valid facility
#       - The activity type does not return a valid activity type object
#       - An activity of the same activity type already exists between the two given times
# If these conditions are met then a new activity instance is created
# [Lewis S]
def create_new_activity(session_type_id: int, activity_type_id: int, facility_name: str, start_time: datetime.datetime, end_time: datetime.datetime):
    facility = edf.return_facility_with_name(facility_name)
    start_time = start_time.replace(second=0, microsecond=0, minute=0, hour=start_time.hour) + datetime.timedelta(hours=start_time.minute//30)
    end_time = end_time.replace(second=0, microsecond=0, minute=0, hour=end_time.hour) + datetime.timedelta(hours=end_time.minute//30)

    if type(session_type_id) is not int:
        log_transaction(f"Failed to add new activity with id {session_type_id} starting on {start_time}: session type id invalid")
        return False
    if type(activity_type_id) is not int:
        log_transaction(f"Failed to add new activity with id {session_type_id} starting on {start_time}: activity_type_id invalid")
        return False
    if end_time > start_time+datetime.timedelta(hours=6) or end_time < start_time+datetime.timedelta(hours=1):
        log_transaction(f"Failed to add new activity with id {session_type_id} starting on {start_time} and ending {end_time}: date times invalid")
        return False
    if end_time.hour < 7 or start_time.hour < 6 or end_time.hour > 22 or start_time.hour > 21:
        log_transaction(f"Failed to add new activity with id {session_type_id} starting on {start_time} and ending {end_time}: date times invalid")
        return False
    if not facility:
        log_transaction(f"Failed to add new activity with id {session_type_id} starting on {start_time}: facility does not exist")
        return False
    if not return_session_type_with_id(session_type_id):
        log_transaction(f"Failed to add new activity with id {session_type_id} starting on {start_time}: session type does not exist")
        return False
    if return_activity_instances_between_dates(session_type_id, start_time, end_time):
        log_transaction(f"Failed to add new activity with id {session_type_id} starting on {start_time}: activity already exists")
        return False

    new_activity = Activity(facility_id=facility.facility_id,
                            session_type_id=session_type_id, activity_type_id=activity_type_id,
                            start_time=start_time, end_time=end_time)

    add_to_database(new_activity)
    log_transaction(f"Added new activity with type_id {session_type_id} starting on {start_time} in facility {facility_name}")
    return new_activity


# Simply returns all activity instances between two datetimes AND in the specified facility_id
# [Lewis S]
def return_activities_between_dates_with_facility_and_activity(start_time: datetime.datetime, end_time: datetime.datetime,
                                                               session_type="Any", facility_id="Any"):
    if session_type == "Any" and facility_id == "Any":
        return Activity.query.filter(Activity.start_time > start_time, Activity.end_time < end_time).all()
    elif session_type == "Any" and facility_id != "Any":
        return Activity.query.filter(Activity.start_time > start_time, Activity.end_time < end_time,
                                     Activity.facility_id == facility_id).all()
    elif facility_id == "Any" and session_type != "Any":
        return Activity.query.filter(Activity.start_time > start_time, Activity.end_time < end_time,
                                     Activity.session_type_id == session_type).all()
    else:
        return Activity.query.filter(Activity.start_time > start_time, Activity.end_time < end_time,
                                     Activity.session_type_id == session_type, Activity.facility_id == facility_id).all()


def return_activities_between_dates_of_activity_type(start_date, end_date, **kwargs):
    """
    :param start_date: The start date of the range of sessions requested
    :param end_date: The end date of the range of sessions requested. Note: This is exclusive.
    :param kwargs: activity_type: an ActivityType object. This is used if supplied.
                   activity_type_id: an int. This is used if activity_type is not supplied.
                   If both activity_type and activity_type_id are not supplied, the activity type will not be filtered.
    :return: A list containing sessions of type "activity_type_id" from start_date to end_date exclusive.
    """
    activity_type = kwargs.get("activity_type")
    activity_type_id = kwargs.get("activity_type_id", None) if activity_type is None else activity_type.activity_type_id

    if activity_type_id is None:
        return Activity.query.filter(Activity.start_time >= start_date, Activity.end_time < end_date).all()
    else:
        return Activity.query.filter(Activity.start_time >= start_date, Activity.end_time < end_date,
                                     Activity.activity_type_id == activity_type_id).all()


def return_weekly_activities_of_type(day: datetime.datetime, session_type_id: int = None):
    """
    :param day: a date that indicates the week of activities desired
    :param session_type_id: The type of the desired activities
    :return: A list containing activities in "day"'s week with the specified activity_type_id
    """
    start_date = day - datetime.timedelta(days=day.weekday())
    end_date = start_date + datetime.timedelta(days=7)

    if session_type_id is None:
        return Activity.query.filter(Activity.start_time >= start_date, Activity.end_time < end_date).all()
    else:
        return Activity.query.filter(Activity.start_time >= start_date, Activity.end_time < end_date,
                                     Activity.session_type_id == session_type_id).all()


def return_session_types_with_activity_type_id(activity_type_id: int):
    return SessionType.query.filter(SessionType.activity_type_id == activity_type_id).all()


def return_activity_type_with_name(activity_type_name: str):
    return ActivityType.query.filter(ActivityType.name == activity_type_name).first()


def return_activity_type_with_id(activity_type_id: str):
    return ActivityType.query.filter(ActivityType.activity_type_id == activity_type_id).first()


# Simply returns an activity with an specific id
# [Lewis S]
def return_activity_with_id(activity_id: int):
    return Activity.query.filter(Activity.activity_id == activity_id).first()


# Returns the max capacity for an activity of a specific session type- this is used for combatting lazy loading
# [Lewis S]
def return_activity_capacity_with_session_type_id(session_type_id):
    session_type: SessionType = SessionType.query.filter(SessionType.session_type_id == session_type_id).first()
    return int(session_type.maximum_activity_capacity)


def return_session_type_capacities():
    """
    :return: a dict of (session_type_id: session_type maximum capacity) for all activity types
    """
    return {session_type.session_type_id: session_type.maximum_activity_capacity for session_type in SessionType.query.filter().all()}


def return_session_type(session_type_id):
    return SessionType.query.filter(SessionType.session_type_id == session_type_id).first()

def return_facilities(facility_id):
    if facility_id == "Any":
        return Facility.query.all()
    return Facility.query.filter(Facility.facility_id == facility_id).all()


def return_regular_activities_before(activity_obj, limit=1000):
    """
    Return a list of "regular activities" with end_time BEFORE the end_time of the activity_obj supplied.
    Activities are "regular" if:
        1. they are of the same activity type
        2. they happen on the weekday (e.g. Monday)
        3. they have the same start and end time
    :param activity_obj: a pivot activity, to specify for the list of regular activities
    :param limit: upper limit of the number of regular activities returned
    """

    num = 0
    activities = []

    next_activity = "gimme more"

    # Get all regular activities before this start date
    while next_activity is not None and num < limit:
        next_activity = Activity.query.filter(
            Activity.session_type_id == activity_obj.session_type_id,
            Activity.start_time >= activity_obj.start_time - datetime.timedelta(days=7 * num),
            Activity.end_time <= activity_obj.end_time - datetime.timedelta(days=7 * num)
        ).first()

        if next_activity is not None:
            activities.append(next_activity)
            num += 1

    # Sort them so the first activity is the oldest activity
    return sorted(activities, key=lambda activity: activity.start_time.strftime("%Y-%m-%d-%H-%M-%S"))


def return_regular_activities_from(activity_obj, limit=2):
    """
    Return a list of "regular activities" FROM the start date of the activity_obj supplied.
    Activities are "regular" if:
        1. they are of the same activity type
        2. they happen on the weekday (e.g. Monday)
        3. they have the same start and end time
    :param activity_obj: a pivot activity, to specify for the list of regular activities
    :param limit: upper limit of the number of regular activities returned
    """
    num = 0
    activities = []

    next_activity = "gimme more"

    while next_activity is not None and num < limit:
        next_activity = Activity.query.filter(
            Activity.session_type_id == activity_obj.session_type_id,
            Activity.start_time >= activity_obj.start_time + datetime.timedelta(days=7 * num),
            Activity.end_time <= activity_obj.end_time + datetime.timedelta(days=7 * num)
        ).first()

        if next_activity is not None:
            activities.append(next_activity)
            num += 1

    return activities


def return_activity_weeks_available(activity_id):
    """
    Based on the time (e.g. Monday 10am-11am) of the activity with id :param activity_id:,
    find the number of consecutive weekly sessions with the same time (i.e. regular).
    """
    activity_obj = Activity.query.filter(Activity.activity_id == activity_id).first()

    return len(return_regular_activities_from(activity_obj, 1000))
