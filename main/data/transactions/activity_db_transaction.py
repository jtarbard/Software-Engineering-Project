# Holds all functions related to the activities of the website and the transactions with the database
import flask
import hashlib
import logging
import datetime
import csv
import main.data.db_session as db

from main.data.db_classes.activity_db_class import ActivityType, Activity
import main.data.transactions.employee_data_transaction as edf

# Logging has been individually set for this file, as transactions in the database
# are important and must be recorded

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/transactions.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(message)s"))

logger.addHandler(file_handler)


# Returns the activity with the same id as the parameter
def return_activity_type_with_id(activity_type_id: int):
    session = db.create_session()
    return session.query(ActivityType).filter(ActivityType.activity_type_id == activity_type_id).first()


# Returns an activity with the same name as the parameter
def return_activity_type_with_name(activity_type_name: str):
    session = db.create_session()
    return session.query(ActivityType).filter(ActivityType.name == activity_type_name.lower()).first()


def add_new_activity(activity_type_id: int, start_datetime: datetime.datetime, end_datetime: datetime.datetime, facility_id: int):
    activity_type = return_activity_type_with_id(activity_type_id)
    if not activity_type:
        return False


# Attempts to add a tag to the list of tags in the csv file, if the tag exists in the csv file then the new tag is
# not added, otherwise the tag is appended to the end of the file
def add_tag(tag: str):
    all_tags = return_valid_tags_from_file()
    if tag.lower() in all_tags:
        return False
    with open("main/data/transactions/valid_tags.csv", "a", newline="") as tag_file:
        tag_writer = csv.writer(tag_file, delimiter=",")
        tag_writer.write(tag)
    return True


# Attempts to remove a tag from the tag_list file, if found then the tag parameter is removed from the file. If
# the tag is not found in the file of tags then the False is returned
def remove_tag(tag: str):
    all_tags = return_valid_tags_from_file()
    try:
        all_tags.remove(tag.lower())
    except ValueError:
        return False
    with open("main/data/transactions/valid_tags.csv", "w+", newline="") as tag_file:
        tag_write = csv.writer(tag_file, delimiter=",")
        tag_write.seek(0)
        tag_write.truncate()
        tag_write.write(all_tags)
    return True


# Returns all the tags from the valid_tags.csv file
def return_valid_tags_from_file():
    all_tags = []
    with open("main/data/transactions/valid_tags.csv", newline="") as tag_file:
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
def return_all_activity_types():
    session = db.create_session()
    return session.query(ActivityType).all()


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

def create_new_activity_type(name: str, description: str, category: str, tags_list: list, miniumum_age: int,
                             maximum_activity_capacity: int, hourly_activity_cost: int, hourly_activity_price: int,
                             valid_composite_roles: int, max_staff: int, min_staff: int):

    if len(name) < 3 or len(name) > 20 or not name.replace(" ", "").isalpha():
        logger.info(f"Failed to add new activity type {name}: name not correct length or type")
        return False
    if len(category) < 4 or len(category) > 20 or not category.replace(" ", "").isalpha():
        logger.info(f"Failed to add new activity type {name}: category not correct length or type")
        return False
    if len(description) < 10 or len(description) > 200:
        logger.info(f"Failed to add new activity type {name}: description not correct length or type")
        return False
    if miniumum_age < 0 or miniumum_age > 100:
        logger.info(f"Failed to add new activity type {name}: maximum_age or miniumum_age not correct size")
        return False
    if maximum_activity_capacity > 150:
        logger.info(f"Failed to add new activity type {name}: maximum_activity_capacity not correct size")
        return False
    if hourly_activity_cost < 0 or hourly_activity_price < 0 or hourly_activity_price > 50 or hourly_activity_cost > 200:
        logger.info(f"Failed to add new activity type {name}: hourly cost or price not correct size")
        return False
    if max_staff > 15 or max_staff < 0 or min_staff < 0 or min_staff > 10:
        logger.info(f"Failed to add new activity type {name}: max_staff or min_staff not correct size")
        return False

    if not check_tags_are_valid(tags_list):
        logger.info(f"Failed to add new activity type {name}: invalid tag instance")
        return False

    tags = ":".join(tags_list)
    if len(tags) > 200:
        logger.info(f"Failed to add new activity type {name}: tag length too long")
        return False

    if not edf.return_roles_from_composition_value(valid_composite_roles):
        logger.info(f"Failed to add new activity type {name}: composite roles are not valid")
        return False

    activity_types = return_all_activity_types()
    for activity in activity_types:
        if activity.name == name.lower():
            logger.info(f"Failed to add new activity type {name}: activity name already exists")
            return False

    new_activity_type = ActivityType()
    new_activity_type.name = name
    new_activity_type.description = description
    new_activity_type.category = category
    new_activity_type.tags = tags
    new_activity_type.minimum_age = miniumum_age
    new_activity_type.maximum_activity_capacity = maximum_activity_capacity
    new_activity_type.hourly_activity_cost = hourly_activity_cost
    new_activity_type.hourly_activity_price = hourly_activity_price
    new_activity_type.valid_composite_roles = valid_composite_roles
    new_activity_type.max_staff = max_staff
    new_activity_type.min_staff = min_staff

    session = db.create_session()
    session.add(new_activity_type)
    logger.info(f"Added new activity {name}")
    session.commit()
    session.close()
    return True