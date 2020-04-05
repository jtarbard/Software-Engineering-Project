import datetime
import pytest

from main.data.db_session import database
from main.data.db_classes.activity_db_class import ActivityType, Activity, Facility
from main.data.db_classes.transaction_db_class import MembershipType


def pytest_generate_tests(metafunc):
    if "basket_cookie_data" in metafunc.fixturenames:
        metafunc.parametrize("basket_cookie_data", range(25), indirect=True)


def create_facilities():
    names = ["Central Hub"]
    descriptions = ["For basket cookies purpose, there is only 1 facility."]
    max_capacities = [314]

    return [ Facility(name=names[i], description=descriptions[i], max_capacity=max_capacities[i])
             for i in range(len(names))]


def create_membership_types():
    names = ["Standard", "Premium"]
    descriptions = ["Standard description", "Premium description"]
    discounts = [30, 100]
    monthly_prices = [3, 10]

    return [ MembershipType(name=names[i], description=descriptions[i],
                            discount=discounts[i], monthly_price=monthly_prices[i])
             for i in range(len(names)) ]


def create_activity_types():
    names = ["ActivityType1", "ActivityType2", "ActivityType3"]
    descriptions = ["ActivityType1 description", "ActivityType2 description", "ActivityType3 description"]
    categories = ["Category1", "Category2", "Category3"]
    tags_list = ["tag1:tag2", "tag2:tag4", "tag3:tag4"]
    minimum_ages = [1, 2, 3]
    maximum_activity_capacities = [100, 200, 300]
    hourly_activity_costs = [4, 5, 6]
    hourly_activity_prices = [40, 50, 60]
    min_staffs = [10, 20, 30]
    max_staffs = [40, 50, 60]

    return [ ActivityType(name=names[i], description=descriptions[i], category=categories[i],
                          tags=tags_list[i], minimum_age=minimum_ages[i],
                          maximum_activity_capacity=maximum_activity_capacities[i],
                          hourly_activity_cost=hourly_activity_costs[i],
                          hourly_activity_price=hourly_activity_prices[i],
                          max_staff=max_staffs[i], min_staff=min_staffs[i])
             for i in range(len(names)) ]


def create_activities():
    facility_ids = [1]
    activity_type_ids = [1, 2, 3]
    start_times = [datetime.datetime.today()]
    end_times = [datetime.datetime.today()+datetime.timedelta(hours=1)]

    return [ Activity(facility_id=facility_ids[0], activity_type_id=activity_type_ids[i],
                      start_time=start_times[0], end_time=end_times[0])
             for i in range(len(activity_type_ids)) ]


facility_objs, membership_type_objs, activity_type_objs, activity_objs = None, None, None, None


@pytest.yield_fixture(scope="function")
def populate_basket_cookies_db():
    global facility_objs, membership_type_objs, activity_type_objs, activity_objs

    database.session.begin_nested()

    facility_objs = create_facilities()
    membership_type_objs = create_membership_types()
    activity_type_objs = create_activity_types()
    activity_objs = create_activities()

    [database.session.add(facility) for facility in facility_objs]
    [database.session.add(membership_type) for membership_type in membership_type_objs]
    [database.session.add(activity_type) for activity_type in activity_type_objs]
    [database.session.add(activity) for activity in activity_objs]

    yield database

    database.session.rollback()


@pytest.fixture
def basket_cookie_data(request):
    global facility_objs, membership_type_objs, activity_type_objs, activity_objs

    if facility_objs is None:
        facility_objs = create_facilities()
        membership_type_objs = create_membership_types()
        activity_type_objs = create_activity_types()
        activity_objs = create_activities()

    data = [("", (False, None, None, None)),              # Empty basket - Invalid (if it were valid, empty receipts could be created)
            ("A:1", (True, [activity_objs[0]], None, None)),    # 1 Valid Activity
            ("M:1:3", (True, [], membership_type_objs[0], 3)),  # 1 Valid Membership
            ("A:1;M:1:3", (True, [activity_objs[0]], membership_type_objs[0], 3)),  # 1 Valid Activity and 1 Valid Membership
            ("A:1;A:2;A:3", (True, [activity_objs[0], activity_objs[1], activity_objs[2]], None, None)),  # 3 valid activities
            ("A:1;A:1", (True, [activity_objs[0], activity_objs[0]], None, None)),   # 2 of the same Activity
            ("M:1:128", (True, [], membership_type_objs[0], 128)),  # 1 Valid Membership with long duration
            ("A:4", (False, None, None, None)),           # 1 invalid activity (over maximum)
            ("A:0", (False, None, None, None)),           # 1 invalid activity (0)
            ("A:-1", (False, None, None, None)),          # 1 invalid activity (negative)
            ("A:1:1", (False, None, None, None)),         # 1 invalid activity (invalid format - indicating activity with duration)
            ("A:1:1:1", (False, None, None, None)),       # 1 invalid activity (invalid format - too many segments)
            ("M:3:1", (False, None, None, None)),         # 1 invalid membership (over maximum)
            ("M:0:1", (False, None, None, None)),         # 1 invalid membership (0)
            ("M:0", (False, None, None, None)),           # 1 invalid membership (missing duration)
            ("M:0:0", (False, None, None, None)),         # 1 invalid membership (0 duration)
            ("M:0:-1", (False, None, None, None)),        # 1 invalid membership (negative duration)
            ("M:0:1:1", (False, None, None, None)),       # 1 invalid membership (invalid format - too many segments)
            ("M:-1:1", (False, None, None, None)),        # 1 invalid membership (negative)
            ("M:0:1;M:1:3", (False, None, None, None)),   # 2 Memberships
            ("M:0:1;M:1:3;M:1:6", (False, None, None, None)),   # Multiple Memberships
            ("M:1:0.5", (False, None, None, None)),       # 1 invalid membership with decimal duration
            ("M:?:1", (False, None, None, None)),         # 1 invalid membership with string type
            ("A:0.5", (False, None, None, None)),         # 1 invalid activity with decimal type
            ("A:?", (False, None, None, None))            # 1 invalid activity with string type
            ]

    return data[request.param]
