# Holds all functions related to the users of the website and the transactions with the database
import random
import flask
import hashlib
import logging
import datetime
from datetime import timedelta
import main.data.db_session as db
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.employee_data_transaction as edf
import main.data.transactions.transaction_db_transaction as tdf
from main.data.db_classes.activity_db_class import *
from main.data.db_classes.employee_data_db_class import *
from main.data.db_classes.transaction_db_class import *
from main.data.db_classes.user_db_class import *


from flask import Response
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from main.data.db_classes.user_db_class import Customer, User, Employee, Manager

# Logging has been individually set for this file, as transactions in the database
# are important and must be recorded

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/transactions.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(message)s"))

logger.addHandler(file_handler)


# Populates the database with all the facilities in out leisure center
def create_facilities():
    logger.info("Creating database facilities:")

    facility_num = 8
    session = db.create_session()
    facilities = [Facility() for i in range(facility_num)]

    names = [
        "Main Swimming Pool", "Gym", "Sports Hall 1",
        "Sports Hall 2", "Climbing Wall", "Tennis Courts",
        "Outside Playing Field", "Studio Room"
    ]

    definitions = [
        "Main Swimming Pool description",
        "Gym description",
        "Sports Hall 1 description",
        "Sports Hall 2 description",
        "Climbing Wall description",
        "Tennis Courts description",
        "Outside Playing Field description",
        "Studio Room description"
    ]

    max_capacity = [
        70, 50, 80, 50, 10, 8, 150, 30
    ]

    for i in range(facility_num):
        facilities[i].name = names[i]
        facilities[i].definition = definitions[i]
        facilities[i].max_space = max_capacity[i]
        session.add(facilities[i])
        logger.info(f"Added facility: {facilities[i].name}")

    session.commit()
    session.close()
    return True


# Creates all of the current job roles for staff
def create_roles():
    logger.info("Creating database job roles:")

    role_num = 10
    roles = [Role() for i in range(role_num)]

    names = [
        "Lifeguard","Sports Coach",
        "Instructor","Swim Teacher",
        "Activity Leader","Activity Assistant",
        "Climbing Expert","Trampoline Expert",
        "Martial Arts Expert","Direct Manager"
    ]

    description = [
        "Lifeguard description",
        "Sports Coach description",
        "Instructor description",
        "Swim Teacher description",
        "Activity Leader description",
        "Activity Assistant description",
        "Climbing Expert description",
        "Trampoline Expert description",
        "Martial Arts Expert description",
        "Direct Manager description"
    ]

    hourly_pay = [7.00, 10.00, 10.00, 9.00, 12.00, 9.00, 12.00, 12.00, 11.00, 14.00]


    for i in range(role_num):
        if not edf.create_new_role(names[i], description[i], hourly_pay[i]):
            raise Exception(f"Role with name {names[i]} was invalid")
    return True


# Defines all basic activity types
def create_activity_types():
    logger.info("Creating database activity types:")

    activity_num = 12
    activities = [ActivityType() for i in range(activity_num)]

    names = [
        "Football", "Basketball", "Badminton", "Gym", "Boxing",
        "Climbing", "Cricket", "Tennis", "General Swim",
        "Swimming classes", "Aqua", "Yoga", "Dancing",
        "Trampolining", "Rugby"
    ]

    description = [
        "Football description", "Basketball description",
        "Badminton description", "Gym description",
        "Boxing description", "Climbing description",
        "Cricket description", "Tennis description",
        "General Swim description", "Swimming classes description",
        "Aqua description", "Yoga description",
        "Dancing description", "Trampolining description",
        "Rugby description"
    ]

    category = [
        "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded",
        "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded",
        "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded"
    ]

    set_tags = [""]

    tags = [
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
        ["..."],
    ]

    minimum_age = [12,12,12,16,16,16,14,12,8,0,16,12,8,14,16]

    hourly_activity_cost = [random.randint(3,1000)/100 for i in range(activity_num)]

    hourly_activity_price = [random.randint(5,1500)/100 for i in range(activity_num)]

    max_staff = [6,4,2,4,8,8,4,3,3,8,2,3,4,10,6]

    min_staff = [2,2,1,1,3,4,2,1,1,2,2,1,1,2,2]

    composite_roles = [
        54,  # Sports Coach, Instructor, Activity Leader, Activity Assistant (football)
        54,  # Sports Coach, Instructor, Activity Leader, Activity Assistant (basketball)
        54,  # Sports Coach, Instructor, Activity Leader, Activity Assistant (badminton)
        6,  # Sports Coach, Instructor (gym)
        304,  # Activity Leader, Activity Assistant, Martial Arts Expert (boxing)
        112,  # Activity Leader, Activity Assistant, Climbing Expert (climbing)
        54,  # Sports Coach, Instructor, Activity Leader, Activity Assistant (cricket)
        54,  # Sports Coach, Instructor, Activity Leader, Activity Assistant (tennis)
        1,  # Lifeguard (general swim)
        57,  # Lifeguard, Swim Teacher, Activity Leader, Activity Assistant (swim classes)
        57,  # Lifeguard, Swim Teacher, Activity Leader, Activity Assistant (aqua)
        54,  # Sports Coach, Instructor, Activity Leader, Activity Assistant (yoga)
        54,  # Sports Coach, Instructor, Activity Leader, Activity Assistant (dancing)
        176,  # Activity Leader, Activity Assistant, Trampoline Expert (trampoline)
        54,  # Sports Coach, Instructor, Activity Leader, Activity Assistant (rugby)
    ]

    activity_capacity = [50, 50, 24, 80, 40, 10, 50, 16, 70, 50, 30, 20, 20, 15, 50]

    for i in range(activity_num):
        if not adf.create_new_activity_type(names[i],description[i], category[i], tags[i], minimum_age[i],
                                            activity_capacity[i], hourly_activity_cost[i], hourly_activity_price[i],
                                            composite_roles[i],max_staff[i],min_staff[i]):
            raise Exception(f"Activity with name {names[i]} was invalid")
    return True


# Defines all of the membership types currently available
def create_membership_types():
    logger.info("Creating database membership types:")
    if not tdf.create_new_membership_type("standard", "DescToBeAdded", 30, 15.00) or not tdf.create_new_membership_type("premium", "DescToBeAdded", 100, 30.00):
        raise Exception(f"Membership was invalid")


# Creates a manager account that has access to everything on the website
def create_root_manager_account():
    logger.info("Creating database manager")

    session = db.create_session()

    manager_account = Manager()
    manager_account.country = "uk".lower()
    manager_account.address = "Woodhouse, Leeds".lower()
    manager_account.postal_code = "LS2 9JT".upper()
    manager_account.dob = datetime.today()-timedelta(weeks=52*20)
    manager_account.tel_number = "0113 243 1751"
    manager_account.email = "team_10@leeds.ac.uk".lower()
    manager_account.first_name = "team_10".lower()
    manager_account.last_name = "manager".lower()
    manager_account.title = "Dr".lower()
    manager_account.password = udf.hash_text("Team10")

    session.add(manager_account)
    session.commit()
    session.close()


# Populates the activity table with activities, creates a timetable for the website
def create_pseudorandom_activity_instances(end_date):
    session = db.create_session()
    logger.info(f"Creating timetable between dates: {datetime.today()} and {datetime.today()+end_date}")
    facilities = session.query(Facility).all()
    activity_types = session.query(ActivityType).all()


def populate_db(create_activity_instances):
    if udf.check_user_is_in_database_and_password_valid("team_10@leeds.ac.uk", "Team10"):
        return False
    create_facilities()
    create_roles()
    create_membership_types()
    create_activity_types()
    create_root_manager_account()
    if create_activity_instances:
        create_pseudorandom_activity_instances(end_date=timedelta(weeks=4))
    return True
