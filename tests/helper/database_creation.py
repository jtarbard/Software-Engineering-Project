import datetime
import pytest

from main.data.db_session import database

from main.data.db_classes.transaction_db_class import MembershipType, Membership, PaymentDetails, Receipt, Booking
from main.data.db_classes.employee_data_db_class import Employee_Router, Role
from main.data.db_classes.activity_db_class import ActivityType, Activity, Facility
from main.data.db_classes.user_db_class import Customer, Employee, Manager

customer_objs = []
employee_objs = []
manager_objs = []
facility_objs = []
membership_type_objs = []
activity_type_objs = []
activity_objs = []


def create_users():
    """
    Creates Customer, Employee, Manager obj, 1 each
    """
    titles = ["Mr", "Mr", "Mrs"]
    passwords = ["passw0rD", "oai9*(13jiovn__eiqf9OIJqlk", "Admin666"]
    first_names = ["John", "FIRSTNAME", "jane"]
    last_names = ["Doe", "LASTNAME", "doe"]
    emails = ["johndoe@thevertex.com", "notsurewhattoexpect@but.hereyougo", "JANEDOE@GMAIL.COM"]
    tels = ["01685469958", "13854685599", "99999999999"]
    bdays = [datetime.datetime(1960, 1, 1), datetime.datetime(1975, 1, 4), datetime.datetime(2004, 3, 22)]
    postcodes = ["W1A 0AX", "DN55 1PT", "EC1A 1BB"]
    addresses = ["3 Clos Waun Wen, Morriston", "The Old Mill, Llwyngwril", "14 Gwyn Drive, Caerphilly"]
    countries = ["GB", "US", "CN"]

    i = 0
    customer_obj = Customer(title=titles[i], password=passwords[i], first_name=first_names[i],
                            last_name=last_names[i], email=emails[i], tel_number=tels[i],
                            dob=bdays[i], postal_code=postcodes[i], address=addresses[i], country=countries[i])
    i = 1
    employee_obj = Employee(title=titles[i], password=passwords[i], first_name=first_names[i],
                            last_name=last_names[i], email=emails[i], tel_number=tels[i],
                            dob=bdays[i], postal_code=postcodes[i], address=addresses[i], country=countries[i])
    i = 2
    manager_obj = Manager(title=titles[i], password=passwords[i], first_name=first_names[i],
                          last_name=last_names[i], email=emails[i], tel_number=tels[i],
                          dob=bdays[i], postal_code=postcodes[i], address=addresses[i], country=countries[i])
    return [customer_obj], [employee_obj], [manager_obj]


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
    end_times = [datetime.datetime.today()+datetime.timedelta(hours=1),
                 datetime.datetime.today()+datetime.timedelta(hours=2),
                 datetime.datetime.today()+datetime.timedelta(hours=3)]

    return [ Activity(facility_id=facility_ids[0], activity_type_id=activity_type_ids[i],
                      start_time=start_times[0], end_time=end_times[i])
             for i in range(len(activity_type_ids)) ]


@pytest.yield_fixture(scope="function")
def populate_database():
    def _add(tables_to_populate: list):
        table_dict = {"facility": facility_objs,
                      "membership_type": membership_type_objs,
                      "activity_type": activity_type_objs,
                      "activity": activity_objs,
                      "customer": customer_objs,
                      "employee": employee_objs,
                      "manager": manager_objs
                      }

        for table in [table for table in tables_to_populate if (table in table_dict.keys())]:
            for obj in table_dict[table]:
                database.session.add(obj)

    return _add


def create_all():
    global facility_objs, membership_type_objs, activity_type_objs, activity_objs, customer_objs, employee_objs, manager_objs

    facility_objs = create_facilities()
    membership_type_objs = create_membership_types()
    activity_type_objs = create_activity_types()
    activity_objs = create_activities()
    customer_objs, employee_objs, manager_objs = create_users()
