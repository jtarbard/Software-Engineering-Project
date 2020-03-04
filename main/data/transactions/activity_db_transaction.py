# Holds all functions related to the activities of the website and the transactions with the database
import datetime
import csv
from main.data.db_session import add_to_database
from main.logger import log_transaction

from main.data.db_classes.activity_db_class import ActivityType, Activity
import main.data.transactions.employee_data_transaction as edf

TAGS_CSV = "main/data/transactions/valid_tags.csv"


# Returns the activity with the same id as the parameter
# [Lewis S]
def return_activity_type_with_id(activity_type_id: int):
    return ActivityType.query.filter(ActivityType.activity_type_id == activity_type_id).first()

# Attempts to return the name of an activity type with a specific activity type ID, this is to combat
# lazy loading errors
# [Lewis S]
def return_activity_type_name_with_activity_type_id(activity_type_id):
    activity_type: ActivityType = ActivityType.query.filter(ActivityType.activity_type_id == activity_type_id).first()
    """
    if not activity_type:
        log_transaction(f"Failed to return activity type name with activity type ID: {activity_type_id} from DB")
    else:
        log_transaction(f"Successfully returned activity type name with activity type ID: {activity_type_id} from DB")
    """
    return str(activity_type.name)


# Returns an activity with the same name as the parameter
# [Lewis S]
def return_activity_type_with_name(activity_type_name: str):
    return ActivityType.query.filter(ActivityType.name == activity_type_name.lower()).first()


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


# Returns all the activity types stored in the database
# [Lewis S]
def return_all_activity_types():
    return ActivityType.query.all()


# Used for creating a new activity type, each of the following parameters are checked as follows:
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
def create_new_activity_type(name: str, description: str, category: str, tags_list: list, miniumum_age: int,
                             maximum_activity_capacity: int, hourly_activity_cost: int, hourly_activity_price: int,
                             max_staff: int, min_staff: int):

    if len(name) < 3 or len(name) > 20 or not name.replace(" ", "").isalpha():
        log_transaction(f"Failed to add new activity type {name}: name not correct length or type")
        return False
    if len(category) < 4 or len(category) > 20 or not category.replace(" ", "").isalpha():
        log_transaction(f"Failed to add new activity type {name}: category not correct length or type")
        return False
    if len(description) < 10 or len(description) > 200:
        log_transaction(f"Failed to add new activity type {name}: description not correct length or type")
        return False
    if miniumum_age < 0 or miniumum_age > 100:
        log_transaction(f"Failed to add new activity type {name}: maximum_age or miniumum_age not correct size")
        return False
    if maximum_activity_capacity > 150:
        log_transaction(f"Failed to add new activity type {name}: maximum_activity_capacity not correct size")
        return False
    if hourly_activity_cost < 0 or hourly_activity_price < 0 or hourly_activity_price > 50 or hourly_activity_cost > 200:
        log_transaction(f"Failed to add new activity type {name}: hourly cost or price not correct size")
        return False
    if max_staff > 15 or max_staff < 0 or min_staff < 0 or min_staff > 10:
        log_transaction(f"Failed to add new activity type {name}: max_staff or min_staff not correct size")
        return False

    if not check_tags_are_valid(tags_list):
        log_transaction(f"Failed to add new activity type {name}: invalid tag instance")
        return False

    tags = ":".join(tags_list)
    if len(tags) > 200:
        log_transaction(f"Failed to add new activity type {name}: tag length too long")
        return False

    activity_types = return_all_activity_types()
    for activity in activity_types:
        if activity.name == name.lower():
            log_transaction(f"Failed to add new activity type {name}: activity name already exists")
            return False

    new_activity_type = ActivityType()
    new_activity_type.name = name.lower()
    new_activity_type.description = description
    new_activity_type.category = category
    new_activity_type.tags = tags
    new_activity_type.minimum_age = miniumum_age
    new_activity_type.maximum_activity_capacity = maximum_activity_capacity
    new_activity_type.hourly_activity_cost = hourly_activity_cost
    new_activity_type.hourly_activity_price = hourly_activity_price
    new_activity_type.max_staff = max_staff
    new_activity_type.min_staff = min_staff

    add_to_database(new_activity_type)
    return True


#  Takes two datetime variables and searches the activity table for a given activity ID that is between the two datetimes.
#  This function will return false if:
#       - The activity type is not an integer
#       - The start and end datetimes are more than 6 hours apart, or are less than an hour apart
#       - The activity type for the given ID could not be returned
#  If these are valid then the table is searched and a list of activity istances are returned
# [Lewis S]
def return_activity_instances_between_dates(activity_type_id: int, start_time: datetime.datetime, end_time: datetime.datetime):
    start_time = start_time.replace(second=0, microsecond=0, minute=0, hour=start_time.hour) + datetime.timedelta(hours=start_time.minute // 30)
    end_time = end_time.replace(second=0, microsecond=0, minute=0, hour=end_time.hour) + datetime.timedelta(hours=end_time.minute // 30)

    if type(activity_type_id) is not int:
        log_transaction(
            f"Failed to return activity with id {activity_type_id} starting on {start_time}: facility id or activity type id invalid")
        return False
    if end_time > start_time + datetime.timedelta(hours=6) or end_time < start_time + datetime.timedelta(hours=1):
        log_transaction(
            f"Failed to return activity with id {activity_type_id} starting on {start_time}: date times invalid")
        return False
    if not return_activity_type_with_id(activity_type_id):
        log_transaction(
            f"Failed to return activity with id {activity_type_id} starting on {start_time}: activity type does not exist")
        return False

    return Activity.query.filter(Activity.activity_type_id == activity_type_id,
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
def create_new_activity(activity_type_id: int, facility_name: str, start_time: datetime.datetime, end_time: datetime.datetime):
    facility = edf.return_facility_with_name(facility_name)
    start_time= start_time.replace(second=0, microsecond=0, minute=0, hour=start_time.hour) + datetime.timedelta(hours=start_time.minute//30)
    end_time= end_time.replace(second=0, microsecond=0, minute=0, hour=end_time.hour) + datetime.timedelta(hours=end_time.minute//30)

    if type(activity_type_id) is not int:
        log_transaction(f"Failed to add new activity with id {activity_type_id} starting on {start_time}: activity type id invalid")
        return False
    if end_time > start_time+datetime.timedelta(hours=6) or end_time < start_time+datetime.timedelta(hours=1):
        log_transaction(f"Failed to add new activity with id {activity_type_id} starting on {start_time} and ending {end_time}: date times invalid")
        return False
    if end_time.hour < 7 or start_time.hour < 6 or end_time.hour > 22 or start_time.hour > 21:
        log_transaction(f"Failed to add new activity with id {activity_type_id} starting on {start_time} and ending {end_time}: date times invalid")
        return False
    if not facility:
        log_transaction(f"Failed to add new activity with id {activity_type_id} starting on {start_time}: facility does not exist")
        return False
    if not return_activity_type_with_id(activity_type_id):
        log_transaction(f"Failed to add new activity with id {activity_type_id} starting on {start_time}: activity type does not exist")
        return False
    if return_activity_instances_between_dates(activity_type_id, start_time, end_time):
        log_transaction(f"Failed to add new activity with id {activity_type_id} starting on {start_time}: activity already exists")
        return False

    new_activity = Activity()
    new_activity.facility_id = facility.facility_id
    new_activity.activity_type_id = activity_type_id
    new_activity.start_time = start_time
    new_activity.end_time = end_time

    add_to_database(new_activity)
    log_transaction(f"Added new activity with id {activity_type_id} starting on {start_time} in facility {facility_name}")
    return True


# Simply returns all activity instances between two datetimes
# [Lewis S]
def return_activities_between_dates(start_date: datetime.datetime, end_time: datetime.datetime):
    return Activity.query.filter(Activity.start_time > start_date, Activity.end_time < end_time).all()


# Simply returns an activity with an specific id
# [Lewis S]
def return_activity_with_id(activity_id: int):
    return Activity.query.filter(Activity.activity_id == activity_id).first()


# Returns the max capacity for an activity of a specific type- this is used for combatting lazy loading
# [Lewis S]
def return_activity_capacity_with_activity_type_id(activity_type_id):
    activity_type: ActivityType= ActivityType.query.filter(ActivityType.activity_type_id == activity_type_id).first()
    return int(activity_type.maximum_activity_capacity)