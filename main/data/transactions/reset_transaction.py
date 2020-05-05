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
             description="The competition standard 50m, eight lane swimming pool is the ideal space for swimmers of all ages and abilities to enjoy.",
             max_capacity=70,
             base_facility_price=70.00),
        dict(name="Fitness Room",
             description="The contemporary 100-station fitness room features an extensive range of cardiovascular and resistance machines and dedicated free-weight areas.",
             max_capacity=120,
             base_facility_price=0),
        dict(name="Apex Sports Hall",
             description="The new 120m Apex Sports Hall is home to an indoor football pitch, basketball courts, badminton courts, and our gymnastics and boxing classes.",
             max_capacity=800,
             base_facility_price=40.00),
        dict(name="Edge Sports Hall",
             description="The 60m Edge Sports Hall is home to basketball courts, badminton courts, and our gymnastics and boxing classes.",
             max_capacity=500,
             base_facility_price=25.00),
        dict(name="Climbing Wall",
             description="The 10m climbing wall features 10 belay lines, a bouldering cave and a separate teaching wall. It is designed for beginners and experts alike.",
             max_capacity=18,
             base_facility_price=35.00),
        dict(name="Tennis Court",
             description="The outdoor modern hard surface tennis courts are fitted with state of the art floodlighting and is ready all year round.",
             max_capacity=8,
             base_facility_price=15.00),
        dict(name="Squash Court",
             description="The glass backed competition standard squash courts are ideal for both leisure and competitive play.",
             max_capacity=4,
             base_facility_price=15.00),
        dict(name="Outside Playing Field",
             description="The 4 acre floodlight-lit outside playing field is maintained all year round and host to cricket grounds, two football pitches, and a rugby pitch.",
             max_capacity=150,
             base_facility_price=30.00),
        dict(name="Studio",
             description="The ultra-modern large studio is home to a wall of full height mirrors and state of the art adaptive lighting to suite any activity.",
             max_capacity=30,
             base_facility_price=35.00)
    ]

    for item in data:
        facility_type = FacilityType(facility_type_name=item["name"],
                                     description=item["description"],
                                     max_capacity=item["max_capacity"],
                                     base_facility_price=item["base_facility_price"])
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
        "Climbing Expert", "Gymnastics Expert",
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
        "Gymnastics Expert description",
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
    Define and add all activity types in the database.
    ActivityType are, for example, "Tennis", "Basketball", "Yoga" (loosely, the "Sports" name);
    whereas SessionType (previously ActivityType) are, for example, "Tennis Team Event".
    """
    names = [
        "Football", "Basketball", "Badminton", "General Fitness", "Boxing", "Climbing", "Cricket", "Tennis", "Squash",
        "Swimming", "Aqua", "Yoga", "Dancing", "Gymnastics", "Rugby"
    ]

    for name in names:
        activity_type = ActivityType(name=name)
        if not add_to_database(activity_type):
            log_transaction(f"Failed to add activity type: {activity_type}")
            return False
    return True


def create_session_types():
    """
    Defines all basic session types. These are the types a session can be. For example, "Tennis Team Event".
    """

    log_transaction("Creating database session types:")

    # TODO: We should try to convert the individual lists into this format.
    # data = [
    #     dict(activity_type_name="Football",
    #          name="Football Classes",
    #          description="Football classes are led by FA qualified coaches and are designed to establish core skills and develop intermediate talent in an engaging and fun manner. Whatever your skill set our coaches are here to assist you." ,
    #          category="TBA",
    #          tags=["Ball Games", "Class"]
    #     )
    # ]

    activity_type_names = [
        "Football", "Basketball", "Badminton",
        "General Fitness", "Boxing", "Climbing", "Cricket",
        "Tennis", "Tennis", "Squash", "Squash",
        "Swimming", "Swimming", "Aqua",
        "Yoga", "Dancing", "Gymnastics", "Rugby"
    ]

    names = [
        "Football Classes", "Basketball Classes", "Badminton Classes",
        "General Fitness", "Boxing Classes", "Climbing Sessions", "Cricket Classes",
        "Tennis Sessions", "Tennis Team Events", "Squash Sessions", "Squash Team Events",
        "General Swim", "Swimming Classes", "Aqua Classes",
        "Yoga Classes", "Dancing Classes", "Gymnastics Classes", "Rugby Classes"
    ]

    activity_num = len(names)

    description = [
        "Football classes are led by FA qualified coaches and are designed to establish core skills and develop intermediate talent in an engaging and fun manner. Whatever your skill set our coaches are here to assist you." ,
        "Basketball classes are led by accredited coaches and are designed to establish core skills and develop intermediate talent in an engaging and fun manner. Whatever your skill set our coaches are here to assist you.",
        "Badminton classes are led by accredited coaches and are catered to your needs. Whether you need to establish core skills, develop intermediate talent, or refine expertise, our coaches are here to help you achieve.",
        "General fitness sessions provide access to our state of the art fitness suite with a wide range of cardiovascular, resistance, and weight facilities, with support from our trained staff.",
        "Our boxing classes are led by accredited coaches and are catered to your needs. Whether you need to establish core skills, develop intermediate talent, or refine expertise, our coaches are here to help you achieve.",
        "Climbing sessions provide access to our 10m climbing wall with 10 belay lines, a bouldering cave and separate teaching wall. Whether you're an experience climber or complete novice, our instructors are around to guide you.",
        "Cricket classes are led by accredited coaches and are catered to your needs. Whether you need to establish core skills, develop intermediate talent, or refine expertise, our coaches are here to help you achieve.",
        "Tennis sessions provide private access to our modern hard surface outdoor tennis courts. Equipment is available for rent at the reception.",
        "Tennis team events are host to local and national league and competitive games. If you are involved in a league or wish to host a competitive match, you can book for a team session here.",
        "Squash sessions provide private access to our glass backed competition standard squash courts. Equipment is available for rent at the reception.",
        "Squash team events are host to local and national league and competitive games. If you are involved in a league or wish to host a competitive match, you can book for a team session here.",
        "General swim sessions are held in our 50m pool with eight lanes for exercise and practice. Alternatively, we have an open section for fun, unrestricted general swim. Whether you are coming alone or as a group, this is for you!",
        "Swimming classes are led by qualified instructors and are designed to establish core skills in an engaging and fun manner. No matter your skill, our instructors are here to help.",
        "Aqua classes are held in our 50m swimming pool, led by our well-loved instructors. They are designed to give a light and fun workout. It is an ideal exercise for those with restricted mobility or joint pain.",
        "Yoga classes are held in our ultra-modern studio and are led by highly-experienced and well-loved instructors. With adaptive mood lighting and dampened acoustics, our yoga classes is a marvellous option for relaxation.",
        "Dance classes provide carefully crafted high-intensity workouts designed to give you a full-body workout, while you loose yourself to dance.",
        "Our mixed gender artistic gymnastics classes are led by nationally recognised instructors and are designed to support both core skill development and intermediate refinement.",
        "Rugby classes are led by qualified coaches and are designed to establish core skills and develop intermediate talent in an engaging and fun manner. Whatever your skill set, our coaches are here to assist you."
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

    minimum_age = [6, 12, 12, 16, 16, 16, 14, 12, 12, 12, 12,  8, 0, 16, 12, 8, 14, 16]

    hourly_activity_cost = [random.randint(100, 250) / 100 for i in range(activity_num)]

    hourly_activity_price = [(random.randint(150, 600) / 100) + hourly_activity_cost[i] for i in range(activity_num)]

    max_staff = [6, 4, 2, 4, 8, 8, 4, 1, 3, 1, 2, 3, 8, 2, 3, 4, 10, 6]

    min_staff = [2, 2, 1, 1, 3, 4, 2, 0, 1, 0, 1, 1, 2, 2, 1, 1, 2, 2]

    activity_capacity = [50, 50, 24, 120, 40, 10, 50, 4, 16, 4, 10, 70, 50, 30, 20, 20, 15, 50]

    for i in range(activity_num):
        if not adf.create_new_session_type(activity_type_names[i].lower(), names[i], description[i], category[i],
                                           tags[i], minimum_age[i], activity_capacity[i],
                                           hourly_activity_cost[i], hourly_activity_price[i],
                                           max_staff[i], min_staff[i]):
            return False
    return True


def create_activity_facility_relation():
    """
    which session types are available at which facilities (facility object, not type)?
    """

    relationships = [("swimming classes", ["main swimming pool"]),
                     ("basketball classes", ["apex sports hall", "edge sports hall"]),
                     ("football classes", ["apex sports hall", "edge sports hall", "outside playing field"]),
                     ("badminton classes", ["apex sports hall", "edge sports hall"]),
                     ("tennis sessions", ["tennis court 1", "tennis court 2", "tennis court 3", "tennis court 4"]),
                     ("tennis team events", ["tennis court 1", "tennis court 2", "tennis court 3", "tennis court 4"]),
                     ("squash sessions", ["tennis court 1", "tennis court 2", "tennis court 3", "tennis court 4"]),
                     ("squash team events", ["tennis court 1", "tennis court 2", "tennis court 3", "tennis court 4"]),
                     ("general fitness", ["fitness Room"]),
                     ("boxing classes", ["apex sports hall", "edge sports hall"]),
                     ("climbing sessions", ["climbing wall"]),
                     ("cricket classes", ["outside playing field"]),
                     ("yoga classes", ["studio 1", "studio 2"]),
                     ("aqua classes", ["main swimming pool"]),
                     ("general swim", ["main swimming pool"]),
                     ("dancing classes", ["studio 1", "studio 2"]),
                     ("gymnastics classes", ["apex sports hall", "edge sports hall"]),
                     ("rugby classes", ["outside playing field"])]

    for relationship in relationships:
        session_type = SessionType.query.filter(SessionType.session_type_name == relationship[0].lower()).first()
        for facility_name in relationship[1]:
            facility_object = Facility.query.filter_by(name=facility_name.lower()).first()

            # make this facility be available in this session type
            session_type.available_facilities.append(facility_object)
        # update database
        add_to_database(session_type)

    return True


def create_session_type_and_role_validation():

    activity_names_and_roles = {
        "Football Classes": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Basketball Classes": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Badminton Classes": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "General Fitness": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Boxing Classes": ["Activity Leader", "Activity Assistant", "Martial Arts Expert"],
        "Climbing Sessions": ["Activity Leader", "Activity Assistant", "Climbing Expert"],
        "Cricket Classes": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Tennis Sessions": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Tennis Team Events": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Squash Sessions": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Squash Team Events": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "General Swim": ["Lifeguard"],
        "Swimming Classes": ["Lifeguard", "Swim Teacher", "Activity Leader", "Activity Assistant"],
        "Aqua Classes": ["Lifeguard", "Swim Teacher", "Activity Leader", "Activity Assistant"],
        "Yoga Classes": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Dancing Classes": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"],
        "Gymnastics Classes": ["Activity Leader", "Activity Assistant", "Gymnastics Expert"],
        "Rugby Classes": ["Sports Coach", "Instructor", "Activity Leader", "Activity Assistant"]
    }

    for activity in activity_names_and_roles.keys():
        session_type = adf.return_session_type_with_name(activity.lower())
        if not session_type:
            return False
        for role in activity_names_and_roles[activity]:
            role: Role = edf.return_role_id_with_name(role.lower())
            if not role:
                return False
            edf.add_role_to_activity_type(role.role_id, session_type.session_type_id)

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

    session_types = SessionType.query.all()

    if populate_with_random_bookings:
        global customer_account
        customer_account = udf.return_customer_with_email(EMAIL_TYPES["customer"])

    """
    A dictionary of the times of each activity. The key is the session name, the value is another dictionary:
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
        "aqua classes": dict(
            weekday=[[18]],
            weekend=[return_random_times(random.randint(4, 6)),
                     return_random_times(random.randint(4, 6))]
        ),
        "general fitness": dict(
            weekday=[[6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 21]],
            weekend=[[6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 21],
                     [6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 21]]
        ),
        "badminton classes": dict(
            num_sessions_list=[3, 4, 5, 6]
        ),
        "yoga classes": dict(
            num_sessions_list=[3, 4, 5, 6]
        ),
        "tennis sessions": dict(
            num_sessions_list=[2, 3, 4]
        ),
        "football classes": dict(
            num_sessions_list=[2, 3, 4]
        ),
        "basketball classes": dict(
            num_sessions_list=[2, 3, 4]
        ),
        "rugby sessions": dict(
            num_sessions_list=[2, 3, 4]
        )
    }

    for session_type in session_types:
        week_times_dict = activity_times.get(session_type.session_type_name, None)

        if week_times_dict is None:
            # Check whether the session_type has times specified. If not, create them:
            week_times_dict = dict(
                weekday=[return_random_times(random.choice([1, 1, 1, 2, 2, 3])) for i in range(5)],
                weekend=[return_random_times(random.choice([1, 1, 1, 2, 2, 3])) for i in range(2)]
            )
        elif week_times_dict is not None and week_times_dict.get("num_sessions_list") is not None:
            # If the session_type is specified, and "num_sessions" is specified, then create the random times accordingly:
            num_sessions_list = week_times_dict.get("num_sessions_list")
            week_times_dict = dict(
                weekday=[return_random_times(random.choice(num_sessions_list)) for i in range(5)],
                weekend=[return_random_times(random.choice(num_sessions_list)) for i in range(2)]
            )

        weekday_times = week_times_dict.get("weekday", None)
        weekend_times = week_times_dict.get("weekend", None)
        # if even default is not specified, then create a 1-hour session at 8am
        default_times = week_times_dict.get("default", [[8]])

        for day_amount in range(days_between_dates):

            day_index = (current_date + timedelta(days=day_amount)).weekday()

            # weekday
            if day_index not in [5, 6]:
                if weekday_times is not None:
                    times = weekday_times[day_index % len(weekday_times)]
                else:
                    times = default_times[day_index % len(default_times)]

                add_activities_with_times(times, day_amount, session_type, start_date, populate_with_random_bookings)

            # weekend
            else:
                if weekend_times is not None:
                    times = weekend_times[day_index % len(weekend_times)]
                else:
                    times = default_times[day_index % len(default_times)]

                add_activities_with_times(times, day_amount, session_type, start_date, populate_with_random_bookings)


def return_random_times(num_sessions: int):
    """
    Returns random times that activities are assigned to
    :param num_sessions: number of sessions on this day
    """
    returned_times = random.choices([x for x in range(6, 21)], k=num_sessions)
    returned_times.sort()
    returned_times = list(dict.fromkeys(returned_times))
    return returned_times


def add_activities_with_times(returned_times: list, day_amount: int, session_type,
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
    :param session_type: type of the session (e.g. "Tennis classes", "Tennis Team Event")
    :param populate_with_random_bookings: boolean indicating whether random bookings for this activity shall be made.
    """
    for time in returned_times:
        end_time = time + 1
        if time - 1 in returned_times:
            continue
        while end_time in returned_times:
            end_time += 1
        midnight_start_date = datetime.combine(start_date, datetime.min.time())

        facilities_total = len(session_type.available_facilities)
        random_facility = random.randint(0, facilities_total - 1)  # TODO: Make regular session happen in the same facility

        new_activity = adf.create_new_activity(session_type.session_type_id,
                                               session_type.activity_type_id,
                                               session_type.available_facilities[random_facility].name,
                                               midnight_start_date + timedelta(days=day_amount) + timedelta(hours=time),
                                               midnight_start_date + timedelta(days=day_amount) + timedelta(hours=end_time))

        if populate_with_random_bookings and new_activity:
            create_random_bookings(new_activity)


def create_random_bookings(activity: Activity):
    # num_bookings = random.randint(2, activity.session_type.maximum_activity_capacity)
    num_bookings = random.randint(1, 3)
    activities_to_add = []
    for i in range(num_bookings):
        activities_to_add.append(activity)
    tdf.create_new_receipt(basket_activities=activities_to_add, user=customer_account,
                           basket_membership=None, membership_duration=None)


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
        [create_session_types, "failed to create_session_types"],
        [create_activity_facility_relation, "failed to create_activity_facility_relation"],
        [create_base_account_types, "failed to create_base_account_types"],
        [create_session_type_and_role_validation, "failed to create_activity_type_and_role_validation"],
    ]

    for function_list in population_functions:
        if not function_list[0]():
            raise Exception(function_list[1])

    if create_timetable:
        create_pseudorandom_activity_instances(start_date=datetime.today()-timedelta(weeks=2),
                                               end_date=timedelta(weeks=4),
                                               populate_with_random_bookings=populate_with_random_bookings)
    return True
