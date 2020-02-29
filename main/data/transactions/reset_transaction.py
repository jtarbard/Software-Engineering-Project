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
        facilities[i].name = names[i].lower()
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

    activity_num = 15
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

    activity_capacity = [50, 50, 24, 80, 40, 10, 50, 16, 70, 50, 30, 20, 20, 15, 50]

    for i in range(activity_num):
        if not adf.create_new_activity_type(names[i],description[i], category[i], tags[i], minimum_age[i],
                                            activity_capacity[i], hourly_activity_cost[i], hourly_activity_price[i],
                                            max_staff[i],min_staff[i]):
            raise Exception(f"Activity with name {names[i]} was invalid")
    return True


def create_activity_type_and_role_validation():

    activity_names_and_roles = {
        "Football": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Basketball": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Badminton": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Gym": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Boxing": ["Activity Leader", "Activity Assistant", "Martial Arts Expert"],
        "Climbing": ["Activity Leader", "Activity Assistant", "Climbing Expert"],
        "Cricket": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Tennis": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "General Swim": ["Lifeguard"],
        "Swimming classes": ["Lifeguard", "Swim Teacher", "Activity Leader", "Activity Assistant"],
        "Aqua": ["Lifeguard", "Swim Teacher", "Activity Leader", "Activity Assistant"],
        "Yoga": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Dancing": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Trampolining": ["Activity Leader", "Activity Assistant", "Trampoline Expert"],
        "Rugby": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"]
    }

    for activity in activity_names_and_roles.keys():
        activity_type = adf.return_activity_type_with_name(activity.lower())
        if not activity_type:
            raise Exception("Failed to return activity type")
        for role in activity_names_and_roles[activity]:
            role: Role = edf.return_role_id_with_name(role.lower())
            if not role:
                raise Exception("Failed to return role")
            edf.add_role_to_activity_type(role.role_id,activity_type.activity_type_id)


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
    manager_account.email = "team10@leeds.ac.uk".lower()
    manager_account.first_name = "team_10".lower()
    manager_account.last_name = "manager".lower()
    manager_account.title = "Dr".lower()
    manager_account.password = udf.hash_text("WeAreTeam10")

    session.add(manager_account)
    session.commit()
    session.close()


def create_base_employee_and_customer_account():
    udf.create_new_user_account("mr", "WeAreTeam10", "team_10", "customer", "team11@leeds.ac.uk",
                                "0113 243 1751", datetime.today()-timedelta(weeks=52*20), "LS2 9JT",
                                "Woodhouse, Leeds", "uk", 0)
    udf.create_new_user_account("mr", "WeAreTeam10", "team_10", "employee", "team12@leeds.ac.uk",
                                "0113 243 1751", datetime.today() - timedelta(weeks=52*20), "LS2 9JT",
                                "Woodhouse, Leeds", "uk", 1)


# Populates the activity table with semi-random activities, creates a timetable for the website
def create_pseudorandom_activity_instances(end_date: timedelta):
    logger.info(f"Creating timetable between dates: {datetime.today()} and {datetime.today()+end_date}")
    days_between_dates = end_date.days

    current_date = datetime.today()

    session = db.create_session()

    activity_types = session.query(ActivityType).all()

    session.close()

    activity_to_facility_converter = dict.fromkeys([activity_type.name for activity_type in activity_types])

    activity_to_facility_converter["swimming classes"] = ["main swimming pool"]
    activity_to_facility_converter["basketball"] = ["sports hall 1", "sports hall 2", "outside playing field"]
    activity_to_facility_converter["football"] = ["sports hall 1", "sports hall 2", "outside playing field"]
    activity_to_facility_converter["badminton"] = ["sports hall 1", "sports hall 2"]
    activity_to_facility_converter["tennis"] = ["tennis courts"]
    activity_to_facility_converter["gym"] = ["gym"]
    activity_to_facility_converter["boxing"] = ["sports hall 1", "sports hall 2"]
    activity_to_facility_converter["climbing"] = ["climbing wall"]
    activity_to_facility_converter["cricket"] = ["outside playing field"]
    activity_to_facility_converter["yoga"] = ["studio room"]
    activity_to_facility_converter["aqua"] = ["main swimming pool"]
    activity_to_facility_converter["general swim"] = ["main swimming pool"]
    activity_to_facility_converter["dancing"] = ["studio room"]
    activity_to_facility_converter["trampolining"] = ["sports hall 1", "sports hall 2"]
    activity_to_facility_converter["rugby"] = ["outside playing field"]

    for day_amount in range(days_between_dates):
        for activity_type in activity_types:
            if activity_type.name == "general swim":
                if (current_date + timedelta(days=day_amount)).weekday() not in [5, 6]:
                    week_day_times = [6, 7, 8, 13, 14, 15, 16, 17, 20, 21]
                    add_activities_with_times(week_day_times, day_amount, activity_type, activity_to_facility_converter)
                else:
                    amount_today = random.randint(8, 16)
                    returned_times = return_random_times(amount_today)
                    add_activities_with_times(returned_times, day_amount, activity_type, activity_to_facility_converter)

            elif activity_type.name == "swimming classes":
                if (current_date + timedelta(days=day_amount)).weekday() not in [5, 6]:
                    week_day_times = [9, 10, 11, 19]
                    add_activities_with_times(week_day_times, day_amount, activity_type, activity_to_facility_converter)

            elif activity_type.name == "aqua":
                if (current_date + timedelta(days=day_amount)).weekday() not in [5, 6]:
                    week_day_times = [18]
                    add_activities_with_times(week_day_times, day_amount, activity_type, activity_to_facility_converter)
                else:
                    amount_today = random.randint(4, 6)
                    returned_times = return_random_times(amount_today)
                    add_activities_with_times(returned_times, day_amount, activity_type, activity_to_facility_converter)

            elif activity_type.name == "gym":
                week_day_times = [6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 21]
                add_activities_with_times(week_day_times, day_amount, activity_type, activity_to_facility_converter)

            elif activity_type.name in ["badminton", "yoga"]:
                amount_today = random.randint(3, 6)
                returned_times = return_random_times(amount_today)
                add_activities_with_times(returned_times, day_amount, activity_type, activity_to_facility_converter)

            elif activity_type.name in ["tennis", "football", "basketball", "rugby"]:
                amount_today = random.randint(2, 4)
                returned_times = return_random_times(amount_today)
                add_activities_with_times(returned_times, day_amount, activity_type, activity_to_facility_converter)

            else:
                amount_today = random.choices([1, 1, 1, 2, 2, 3], k=1)[0]
                returned_times = return_random_times(amount_today)
                add_activities_with_times(returned_times, day_amount, activity_type, activity_to_facility_converter)


# Returns random times that activities are assigned to
def return_random_times(amount_today: int):
    returned_times = random.choices([x for x in range(6, 21)], k=amount_today)
    returned_times.sort()
    returned_times = list(dict.fromkeys(returned_times))
    return returned_times


# Traverses the times an activity takes place and adds it to the database
def add_activities_with_times(returned_times: list, day_amount: int, activity_type, activity_to_facility_converter: dict):
    for time in returned_times:
        end_time = time + 1
        if time - 1 in returned_times:
            continue
        while end_time in returned_times:
            end_time += 1
        midnight_today = datetime.combine(datetime.today(), datetime.min.time())
        facility_to_use = random.randint(0, len(activity_to_facility_converter[activity_type.name])-1)
        adf.create_new_activity(activity_type.activity_type_id,
                                activity_to_facility_converter[activity_type.name][facility_to_use],
                                midnight_today + timedelta(days=day_amount) + timedelta(hours=time),
                                midnight_today + timedelta(days=day_amount) + timedelta(hours=end_time))


# Executes all the functions for populating the database
def populate_db(create_activity_instances):
    if udf.check_user_is_in_database_and_password_valid("team10@leeds.ac.uk", "WeAreTeam10"):
        return False
    create_facilities()
    create_roles()
    create_membership_types()
    create_activity_types()
    create_activity_type_and_role_validation()
    create_base_employee_and_customer_account()
    create_root_manager_account()
    if create_activity_instances:
        create_pseudorandom_activity_instances(end_date=timedelta(weeks=1))
    return True
