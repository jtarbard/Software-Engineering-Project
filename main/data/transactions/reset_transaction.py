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


# For demo purpose
EMAIL_TYPES = {
    "customer": "team_10_c@leeds.ac.uk",
    "employee": "team_10_e@leeds.ac.uk",
    "manager": "team_10_m@leeds.ac.uk"
}
PASSWORD = "WeAreTeam10"
customer_account = None


def create_facility_types():
    """
    TODO: doc
    """

    # These are the "facilities" that will show up in the Facilities page on the website. They define the generic type
    # of a type of facility
    data = [
        dict(name="Swimming Pool",
             description="Our competition standard 50m, eight lane swimming pool is the ideal space for swimmers of all ages and abilities to enjoy.",
             max_capacity=70),
        dict(name="Fitness Room",
             description="Our contemporary 100-station itness room features an extensive range of cardiovascular and resistance machines and dedicated free-weight areas.",
             max_capacity=120),
        dict(name="Apex Sports Hall",
             description="Our 120m apex sports hall is home to some of our football, basketball, badminton, trampolining, and boxing classes.",
             max_capacity=80),
        dict(name="Edge Sports Hall",
             description="Our 60m edge sports hall is home to some of our basketball, badminton, trampolining, and boxing classes.",
             max_capacity=50),
        dict(name="Climbing Wall",
             description="Climbing Wall description",
             max_capacity=10),
        dict(name="Tennis Court",
             description="Tennis Court description",
             max_capacity=8),
        dict(name="Squash Court",
             description="Squash Court description",
             max_capacity=4),
        dict(name="Outside Playing Field",
             description="Outside Playing Field description",
             max_capacity=150),
        dict(name="Studio",
             description="Studio description",
             max_capacity=30)
    ]

    for item in data:
        facility_type = FacilityType(facility_type_name=item["name"],
                                     description=item["description"],
                                     max_capacity=item["max_capacity"])
        if not add_to_database(facility_type):
            log_transaction(f"Failed to add facility type: {facility_type}")
            return False
    return True


def create_facilities():
    """
    Populates the database with all the facilities in our leisure center, The Vertex
    """

    facility_and_type_dict = {
        "Main Swimming Pool": "Swimming Pool",
        "Fitness Room": "Fitness Room",
        "Apex Sports Hall": "Apex Sports Hall",
        "Edge Sports Hall": "Edge Sports Hall",
        "Climbing Wall": "Climbing Wall",
        "Tennis Court 1": "Tennis Court",
        "Tennis Court 2": "Tennis Court",
        "Tennis Court 3": "Tennis Court",
        "Tennis Court 4": "Tennis Court",
        "Squash Court 1": "Squash Court",
        "Squash Court 2": "Squash Court",
        "Squash Court 3": "Squash Court",
        "Squash Court 4": "Squash Court",
        "Outside Playing Field": "Outside Playing Field",
        "Studio 1": "Studio",
        "Studio 2": "Studio"
    }

    for facility_name, facility_type in facility_and_type_dict.items():
        facility = Facility(name=facility_name,
                            facility_type_id=adf.return_facility_type_with_name(facility_type).facility_type_id)
        if not add_to_database(facility):
            log_transaction(f"Failed to add facility: {facility}")
            return False
    return True


def create_roles():
    """
    Creates all of the current job roles for staff
    """

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


def create_activity_types():
    """
    Defines all basic activity types
    """

    log_transaction("Creating database activity types:")

    names = [
        "Football", "Basketball", "Badminton",
        "General Fitness", "Boxing", "Climbing", "Cricket",
        "Tennis Session", "Tennis Team Event",
        "Squash Session", "Squash Team Event",
        "General Swim", "Swimming classes", "Aqua",
        "Yoga", "Dancing",
        "Trampolining", "Rugby"
    ]

    activity_num = len(names)

    description = [
        "Football description", "Basketball description",
        "Badminton description", "General Fitness description",
        "Boxing description", "Climbing description",
        "Cricket description", "Tennis description",
        "Tennis description", "Squash description",
        "Squash description",
        "General Swim description", "Swimming classes description",
        "Aqua description", "Yoga description",
        "Dancing description", "Trampolining description",
        "Rugby description"
    ]

    category = [
        "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded",
        "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded",
        "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded", "ToBeAdded",
        "ToBeAdded", "ToBeAdded", "ToBeAdded",
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
        ["..."],
        ["..."],
        ["..."],
    ]

    minimum_age = [12, 12, 12, 16, 16, 16, 14, 12, 12, 12, 12,  8, 0, 16, 12, 8, 14, 16]

    hourly_activity_cost = [random.randint(100, 250) / 100 for i in range(activity_num)]

    hourly_activity_price = [(random.randint(150, 600) / 100) + hourly_activity_cost[i] for i in range(activity_num)]

    max_staff = [6, 4, 2, 4, 8, 8, 4, 1, 3, 1, 2, 3, 8, 2, 3, 4, 10, 6]

    min_staff = [2, 2, 1, 1, 3, 4, 2, 0, 1, 0, 1, 1, 2, 2, 1, 1, 2, 2]

    activity_capacity = [50, 50, 24, 120, 40, 10, 50, 4, 16, 4, 10, 70, 50, 30, 20, 20, 15, 50]

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
        "General Fitness": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Boxing": ["Activity Leader", "Activity Assistant", "Martial Arts Expert"],
        "Climbing": ["Activity Leader", "Activity Assistant", "Climbing Expert"],
        "Cricket": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Tennis Session": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Tennis Team Event": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Squash Session": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Squash Team Event": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
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


def create_pseudorandom_activity_instances(start_date: datetime.date, end_date: timedelta,
                                           populate_with_random_bookings: bool):
    """
    Populates the activity table with semi-random activities, creating a timetable for the website.
    The sessions are the same every week in order to satisfy the "regular discount" requirement. The sessions in a week
    are still random.
    """
    log_transaction(f"Creating timetable between dates: {start_date} and {start_date + end_date}")
    days_between_dates = end_date.days

    current_date = start_date

    activity_types = ActivityType.query.all()

    if populate_with_random_bookings:
        global customer_account
        customer_account = udf.return_customer_with_email(EMAIL_TYPES["customer"])

    """
    A dictionary of the times of each activity. The key is the activity name, the value is another dictionary:
    If a key is specified with an empty list, it will get registered as an empty day (i.e. no session on that day).
    Each key has a list of lists. The innermost list represents the spanning hours of the activity on some days.
        weekday: from Monday to Friday, cycled.
        weekend: on Saturday and Sunday.
                 the random.randint() thing is for randomizing the number of sessions.
        default: on unspecified days, cycled.
         
    Cycled lists (weekday and default) Does not need to contain the exact number of lists. 
    Under-specified lists are cycled, and over-specified lists are unused.
    For example, if weekday is not specified, and "default" contains this - [listA, listB, listC],
    the times from Monday to Friday would be listA, listB, listC, listA, listB.
    """
    activity_times = {
        "general swim": dict(
            weekday=[[6, 7, 8, 13, 14, 15, 16, 17, 20, 21]],
            weekend=[return_random_times(random.randint(8, 16)),
                     return_random_times(random.randint(8, 16))]  # the two days have different times
        ),
        "swimming classes": dict(
            weekday=[[9, 10, 11, 19]],
            weekend=[[]]
        ),
        "aqua": dict(
            weekday=[[18]],
            weekend=[return_random_times(random.randint(4, 6)),
                     return_random_times(random.randint(4, 6))]
        ),
        "general fitness": dict(
            weekday=[[6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 21]],
            weekend=[[6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 21],
                     [6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 21]]
        ),
        "badminton": dict(
            default=[return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6))]
        ),
        "yoga": dict(
            default=[return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6)),
                     return_random_times(random.randint(3, 6))]
        ),
        "tennis": dict(
            default=[return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4))]
        ),
        "football": dict(
            default=[return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4))]
        ),
        "basketball": dict(
            default=[return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4))]
        ),
        "rugby": dict(
            default=[return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4)),
                     return_random_times(random.randint(2, 4))]
        ),
        "default": dict(
            default=[return_random_times(random.choice([1, 1, 1, 2, 2, 3])),
                     return_random_times(random.choice([1, 1, 1, 2, 2, 3])),
                     return_random_times(random.choice([1, 1, 1, 2, 2, 3])),
                     return_random_times(random.choice([1, 1, 1, 2, 2, 3])),
                     return_random_times(random.choice([1, 1, 1, 2, 2, 3])),
                     return_random_times(random.choice([1, 1, 1, 2, 2, 3])),
                     return_random_times(random.choice([1, 1, 1, 2, 2, 3]))]
        )
    }

    for activity_type in activity_types:
        week_times_dict = activity_times.get(activity_type.name, activity_times["default"])
        weekday_times = week_times_dict.get("weekday", None)
        weekend_times = week_times_dict.get("weekend", None)
        # if even default is not specified, then create a 1-hour session at 8am
        default_times = week_times_dict.get("default", [[8]])
        # this increments by one whenever a weekday/weekend's time is not specified via weekday_times or weekend_times
        unspecified_days_index = 0

        for day_amount in range(days_between_dates):

            day_index = (current_date + timedelta(days=day_amount)).weekday()

            # weekday
            if day_index not in [5, 6]:
                if weekday_times is not None:
                    times = weekday_times[day_index % len(weekday_times)]
                else:
                    times = default_times[unspecified_days_index % len(default_times)]
                    unspecified_days_index += 1

                add_activities_with_times(times, day_amount, activity_type, start_date, populate_with_random_bookings)

            # weekend
            else:
                if weekend_times is not None:
                    times = weekend_times[day_index % len(weekend_times)]
                else:
                    times = default_times[unspecified_days_index % len(default_times)]
                    unspecified_days_index += 1

                add_activities_with_times(times, day_amount, activity_type, start_date, populate_with_random_bookings)

            if day_index >= 6:
                unspecified_days_index = 0  # restart the cycle for setting the session times on unspecified days


def return_random_times(num_sessions: int):
    """
    Returns random times that activities are assigned to
    :param num_sessions: number of sessions on this day
    """
    returned_times = random.choices([x for x in range(6, 21)], k=num_sessions)
    returned_times.sort()
    returned_times = list(dict.fromkeys(returned_times))
    return returned_times


def add_activities_with_times(returned_times: list, day_amount: int, activity_type,
                              start_date: datetime.date, populate_with_random_bookings):
    """
    Traverses the times an activity takes place and adds it to the database
    :param returned_times: a sorted list of integers from 6 to 21, indicating the start time (i.e. hour) of the activity
                           All activities are at least 1 hour long. The minimum time unit is 1 hour.
                           If there are contiguous integers, such as [2, 3, 4], an activity of time 2-4 will be created.
                           i.e. Contiguous integers indicates the spanning time of the activity. Alternatively you can
                           think of them as "coagulated" or "gelled" together.
    :param start_date: a pivot date for the activity
    :param day_amount: a positive integer indicating the number of days offset from :param start_date:.
                       Adding :param day_amount: to :param start_date: creates the actual start date for the activity.
    :param activity_type: type of the activity
    :param populate_with_random_bookings: boolean indicating whether random bookings for this activity shall be made.
    """
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
    """
    which activity types are available at which facilities (facility object, not type)?
    """

    relationships = [("swimming classes", ["main swimming pool"]),
                     ("basketball", ["apex sports hall", "edge sports hall", "outside playing field"]),
                     ("football", ["apex sports hall", "edge sports hall", "outside playing field"]),
                     ("badminton", ["apex sports hall", "edge sports hall"]),
                     ("tennis session", ["tennis court 1", "tennis court 2", "tennis court 3", "tennis court 4"]),
                     ("tennis team event", ["tennis court 1", "tennis court 2", "tennis court 3", "tennis court 4"]),
                     ("squash session", ["tennis court 1", "tennis court 2", "tennis court 3", "tennis court 4"]),
                     ("squash team event", ["tennis court 1", "tennis court 2", "tennis court 3", "tennis court 4"]),
                     ("general fitness", ["fitness Room"]),
                     ("boxing", ["apex sports hall", "edge sports hall"]),
                     ("climbing", ["climbing wall"]),
                     ("cricket", ["outside playing field"]),
                     ("yoga", ["studio 1", "studio 2"]),
                     ("aqua", ["main swimming pool"]),
                     ("general swim", ["main swimming pool"]),
                     # ("spin", ["studio 1", "studio 2"]),
                     ("dancing", ["studio 1", "studio 2"]),
                     ("trampolining", ["apex sports hall", "edge sports hall"]),
                     # ("gymnastics", ["apex sports hall", "edge sports hall"]),
                     ("rugby", ["outside playing field"])]

    for relationship in relationships:
        activity_type = ActivityType.query.filter_by(name=relationship[0].lower()).first()
        for facility_name in relationship[1]:
            facility_object = Facility.query.filter_by(name=facility_name.lower()).first()

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
        [create_facility_types, "failed to create facility types"],
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
