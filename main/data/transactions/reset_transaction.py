# Holds all functions related to the users of the website and the transactions with the database
import random
import datetime
from datetime import timedelta
import main.data.db_session as db
import main.data.transactions.user_db_transaction as udf
import main.data.transactions.activity_db_transaction as adf
import main.data.transactions.employee_data_transaction as edf
import main.data.transactions.transaction_db_transaction as tdf
from main.data.db_classes.activity_db_class import *
from main.data.db_classes.employee_data_db_class import *
from main.data.db_classes.user_db_class import Manager
from main.data.db_session import add_to_database
from main.logger import log_transaction


# For debug purpose
EMAIL_TYPES = {
    "customer": "team_10_c@leeds.ac.uk",
    "employee": "team_10_e@leeds.ac.uk",
    "manager": "team_10_m@leeds.ac.uk"
}
PASSWORD = "WeAreTeam10"


# Populates the database with all the facilities in out leisure center
def create_facilities():
    names = [
        "Main Swimming Pool", "Gym", "Sports Hall 1",
        "Sports Hall 2", "Climbing Wall", "Tennis Courts",
        "Outside Playing Field", "Studio Room"
    ]

    descriptions = [
        "Main Swimming Pool description",
        "Gym description",
        "Sports Hall 1 description",
        "Sports Hall 2 description",
        "Climbing Wall description",
        "Tennis Courts description",
        "Outside Playing Field description",
        "Studio Room description"
    ]

    max_capacities = [
        70, 50, 80, 50, 10, 8, 150, 30
    ]

    facilities = [Facility(name=names[i], description=descriptions[i], max_capacity=max_capacities[i])
                  for i in range(len(names))]

    for i, facility in enumerate(facilities):
        if not add_to_database(facility):
            log_transaction(f"Failed to add facility: {names[i]}")
            return False
    return True


# Creates all of the current job roles for staff
def create_roles():
    log_transaction("Creating database job roles:")

    names = [
        "Lifeguard", "Sports Coach",
        "Instructor", "Swim Teacher",
        "Activity Leader", "Activity Assistant",
        "Climbing Expert", "Trampoline Expert",
        "Martial Arts Expert", "Direct Manager"
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

    for i in range(len(names)):
        if not edf.create_new_role(names[i], description[i], hourly_pay[i]):
            return False
    return True


# Defines all basic activity types
def create_activity_types():
    log_transaction("Creating database activity types:")

    names = [
        "Football", "Basketball", "Badminton", "Gym", "Boxing",
        "Climbing", "Cricket", "Tennis", "General Swim",
        "Swimming classes", "Aqua", "Yoga", "Dancing",
        "Trampolining", "Rugby"
    ]

    activity_num = len(names)

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

    minimum_age = [12, 12, 12, 16, 16, 16, 14, 12, 8, 0, 16, 12, 8, 14, 16]

    hourly_activity_cost = [random.randint(3, 250) / 100 for i in range(activity_num)]

    hourly_activity_price = [random.randint(5, 1500) / 100 for i in range(activity_num)]

    max_staff = [6, 4, 2, 4, 8, 8, 4, 3, 3, 8, 2, 3, 4, 10, 6]

    min_staff = [2, 2, 1, 1, 3, 4, 2, 1, 1, 2, 2, 1, 1, 2, 2]

    activity_capacity = [50, 50, 24, 80, 40, 10, 50, 16, 70, 50, 30, 20, 20, 15, 50]

    for i in range(activity_num):
        if not adf.create_new_activity_type(names[i], description[i], category[i], tags[i], minimum_age[i],
                                            activity_capacity[i], hourly_activity_cost[i], hourly_activity_price[i],
                                            max_staff[i], min_staff[i]):
            return False
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
            return False
        for role in activity_names_and_roles[activity]:
            role: Role = edf.return_role_id_with_name(role.lower())
            if not role:
                return False
            edf.add_role_to_activity_type(role.role_id, activity_type.activity_type_id)

    return True


# Defines all of the membership types currently available
def create_membership_types():
    log_transaction("Creating database membership types:")
    return tdf.create_new_membership_type("standard", "DescToBeAdded", 30, 15.00) \
        and tdf.create_new_membership_type("premium", "DescToBeAdded", 100, 30.00)


def create_base_account_types():
    i = 0
    for user_type, email in EMAIL_TYPES.items():
        udf.create_new_user_account(i, title="mr", password=PASSWORD, first_name="team_10", last_name=user_type,
                                    email=email, tel_number="0113 243 1751",
                                    dob=datetime.today()-timedelta(weeks=52*20), postal_code="LS2 9JT",
                                    address="Woodhouse, Leeds", country="uk")
        i += 1
    return True


# Populates the activity table with semi-random activities, creates a timetable for the website
def create_pseudorandom_activity_instances(start_date: datetime.date, end_date: timedelta,
                                           populate_with_random_bookings: bool):
    log_transaction(f"Creating timetable between dates: {start_date} and {start_date + end_date}")
    days_between_dates = end_date.days

    current_date = start_date

    activity_types = ActivityType.query.all()

    if populate_with_random_bookings:
        global customer_account
        customer_account = udf.return_customer_with_email(EMAIL_TYPES["customer"])

    for day_amount in range(days_between_dates):
        for activity_type in activity_types:
            if activity_type.name == "general swim":
                if (current_date + timedelta(days=day_amount)).weekday() not in [5, 6]:
                    week_day_times = [6, 7, 8, 13, 14, 15, 16, 17, 20, 21]
                    add_activities_with_times(week_day_times, day_amount, activity_type, start_date, populate_with_random_bookings)
                else:
                    amount_today = random.randint(8, 16)
                    returned_times = return_random_times(amount_today)
                    add_activities_with_times(returned_times, day_amount, activity_type, start_date, populate_with_random_bookings)

            elif activity_type.name == "swimming classes":
                if (current_date + timedelta(days=day_amount)).weekday() not in [5, 6]:
                    week_day_times = [9, 10, 11, 19]
                    add_activities_with_times(week_day_times, day_amount, activity_type, start_date, populate_with_random_bookings)

            elif activity_type.name == "aqua":
                if (current_date + timedelta(days=day_amount)).weekday() not in [5, 6]:
                    week_day_times = [18]
                    add_activities_with_times(week_day_times, day_amount, activity_type, start_date, populate_with_random_bookings)
                else:
                    amount_today = random.randint(4, 6)
                    returned_times = return_random_times(amount_today)
                    add_activities_with_times(returned_times, day_amount, activity_type, start_date, populate_with_random_bookings)

            elif activity_type.name == "gym":
                week_day_times = [6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 21]
                add_activities_with_times(week_day_times, day_amount, activity_type, start_date, populate_with_random_bookings)

            elif activity_type.name in ["badminton", "yoga"]:
                amount_today = random.randint(3, 6)
                returned_times = return_random_times(amount_today)
                add_activities_with_times(returned_times, day_amount, activity_type, start_date, populate_with_random_bookings)

            elif activity_type.name in ["tennis", "football", "basketball", "rugby"]:
                amount_today = random.randint(2, 4)
                returned_times = return_random_times(amount_today)
                add_activities_with_times(returned_times, day_amount, activity_type, start_date, populate_with_random_bookings)

            else:
                amount_today = random.choice([1, 1, 1, 2, 2, 3])
                returned_times = return_random_times(amount_today)
                add_activities_with_times(returned_times, day_amount, activity_type, start_date, populate_with_random_bookings)


# Returns random times that activities are assigned to
def return_random_times(amount_today: int):
    returned_times = random.choices([x for x in range(6, 21)], k=amount_today)
    returned_times.sort()
    returned_times = list(dict.fromkeys(returned_times))
    return returned_times


# Traverses the times an activity takes place and adds it to the database
def add_activities_with_times(returned_times: list, day_amount: int, activity_type,
                              start_date: datetime.date, populate_with_random_bookings):
    for time in returned_times:
        end_time = time + 1
        if time - 1 in returned_times:
            continue
        while end_time in returned_times:
            end_time += 1
        midnight_start_date = datetime.combine(start_date, datetime.min.time())

        facilities_total = len(activity_type.available_facilities)
        random_facility = random.randint(0, facilities_total - 1)

        new_activity = adf.create_new_activity(activity_type.activity_type_id,
                                activity_type.available_facilities[random_facility].name,
                                midnight_start_date + timedelta(days=day_amount) + timedelta(hours=time),
                                midnight_start_date + timedelta(days=day_amount) + timedelta(hours=end_time))

        if populate_with_random_bookings and new_activity:
            create_random_bookings(new_activity)


def create_random_bookings(activity: Activity):
    num_bookings = random.randint(2, activity.activity_type.maximum_activity_capacity)
    activities_to_add = []
    for i in range(num_bookings):
        activities_to_add.append(activity)
    tdf.create_new_receipt(basket_activities=activities_to_add, user=customer_account,
                           basket_membership=None, membership_duration=None)


def create_activity_facility_relation():
    # which activity types are available at which facilities?

    relationships = [("swimming classes", ["main swimming pool"]),
                     ("basketball", ["sports hall 1", "sports hall 2", "outside playing field"]),
                     ("football", ["sports hall 1", "sports hall 2", "outside playing field"]),
                     ("badminton", ["sports hall 1", "sports hall 2"]),
                     ("tennis", ["tennis courts"]),
                     ("gym", ["gym"]),
                     ("boxing", ["sports hall 1", "sports hall 2"]),
                     ("climbing", ["climbing wall"]),
                     ("cricket", ["outside playing field"]),
                     ("yoga", ["studio room"]),
                     ("aqua", ["main swimming pool"]),
                     ("general swim", ["main swimming pool"]),
                     ("dancing", ["studio room"]),
                     ("trampolining", ["sports hall 1", "sports hall 2"]),
                     ("rugby", ["outside playing field"])]

    for relation in relationships:
        activity_type = ActivityType.query.filter_by(name=relation[0]).first()
        for facility in relation[1]:
            facility_object = Facility.query.filter_by(name=facility).first()

            # make this facility be available in this activity type
            activity_type.available_facilities.append(facility_object)
        # update database
        add_to_database(activity_type)

    return True


# Executes all the functions for populating the database
def populate_db(create_timetable, populate_with_random_bookings):
    # if the manager account exists
    if udf.check_user_is_in_database_and_password_valid(EMAIL_TYPES["manager"], PASSWORD):
        # assume the database has already been populated
        return False

    population_functions = [
        [create_facilities, "failed to create facilities"],
        [create_roles, "failed to create_roles"],
        [create_membership_types, "failed to create create_membership_types"],
        [create_activity_types, "failed to create_activity_types"],
        [create_activity_facility_relation, "failed to create_activity_facility_relation"],
        [create_base_account_types, "failed to create_base_account_types"],
        [create_activity_type_and_role_validation, "failed to create_activity_type_and_role_validation"],
    ]

    for function_list in population_functions:
        if not function_list[0]():
            raise Exception(function_list[1])

    if create_timetable:
        create_pseudorandom_activity_instances(start_date=datetime.today()-timedelta(weeks=2),
                                               end_date=timedelta(weeks=4),
                                               populate_with_random_bookings=populate_with_random_bookings)
    return True
