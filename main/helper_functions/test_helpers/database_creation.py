import datetime
import pytest

from main.data.db_session import database

from main.data.db_classes.transaction_db_class import MembershipType, Membership, PaymentDetails, Receipt, Booking
from main.data.db_classes.employee_data_db_class import Employee_Router, Role
from main.data.db_classes.activity_db_class import ActivityType, Activity, FacilityType, Facility
from main.data.db_classes.user_db_class import Customer, Employee, Manager

# These are created in create_all(), at runtime, before any test is run.
facility_type_objs = []
facility_objs = []
membership_type_objs = []
activity_type_objs = []
activity_objs = []
customer_objs = []
customer_with_membership_objs = []
membership_objs = []
receipt_for_membership_objs = []
employee_objs = []
manager_objs = []


def create_facility_types():
    names = ["Central Hub Type"]
    descriptions = ["For basket cookies purpose, there is only 1 facility."]
    max_capacities = [314]

    return [ FacilityType(facility_type_name=names[i], description=descriptions[i], max_capacity=max_capacities[i])
             for i in range(len(names)) ]


def create_facilities():
    names = ["Central Hub 1"]

    return [ Facility(name=names[i], facility_type_id=1)
             for i in range(len(names)) ]


def create_membership_types():
    names = ["Standard", "Premium"]
    descriptions = ["Standard description", "Premium description"]
    discounts = [30, 100]
    monthly_prices = [3, 10]

    return [ MembershipType(name=names[i], description=descriptions[i],
                            discount=discounts[i], monthly_price=monthly_prices[i])
             for i in range(len(names)) ]


def create_activity_types():
    names = ["ActivityType1", "ActivityType2", "ActivityType3", "VeryCheapActivityType", "VerySmolActivityType"]
    descriptions = ["ActivityType1 description", "ActivityType2 description", "ActivityType3 description", "VeryCheapActivityType description", "VerySmolActivityType description"]
    categories = ["Category1", "Category2", "Category3", "Category3", "Category4"]
    tags_list = ["tag1:tag2", "tag2:tag4", "tag3:tag4", "tag5", "tag2"]
    minimum_ages = [1, 2, 3, 4, 5]
    maximum_activity_capacities = [40, 50, 60, 70, 3]
    hourly_activity_costs = [1, 2, 3, 0.0000011111, 1000]
    hourly_activity_prices = [10, 20, 30, 0.00011111, 1000]
    min_staffs = [1, 2, 3, 4, 5]
    max_staffs = [1, 2, 3, 4, 5]

    return [ ActivityType(name=names[i], description=descriptions[i], category=categories[i],
                          tags=tags_list[i], minimum_age=minimum_ages[i],
                          maximum_activity_capacity=maximum_activity_capacities[i],
                          hourly_activity_cost=hourly_activity_costs[i],
                          hourly_activity_price=hourly_activity_prices[i],
                          max_staff=max_staffs[i], min_staff=min_staffs[i])
             for i in range(len(names)) ]


def create_activities():
    facility_ids = [1]
    activity_type_ids = [1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 4, 4, 5, 5, 5, 1]
    start_times = [datetime.datetime.today()+datetime.timedelta(days=1)]
    end_times = [start_times[0]+datetime.timedelta(hours=1),
                 start_times[0]+datetime.timedelta(hours=2),
                 start_times[0]+datetime.timedelta(hours=3),
                 start_times[0]+datetime.timedelta(hours=24+1),
                 start_times[0]+datetime.timedelta(hours=24+2),
                 start_times[0]+datetime.timedelta(hours=24+3),
                 start_times[0]+datetime.timedelta(hours=48+1),
                 start_times[0]+datetime.timedelta(hours=48+2),
                 start_times[0]+datetime.timedelta(hours=48+3),
                 start_times[0]+datetime.timedelta(hours=1),
                 start_times[0]+datetime.timedelta(hours=24+1),
                 start_times[0]+datetime.timedelta(hours=48+1),
                 start_times[0]+datetime.timedelta(hours=1),
                 start_times[0]+datetime.timedelta(hours=24+1),
                 start_times[0]+datetime.timedelta(hours=48+1),
                 start_times[0]+datetime.timedelta(hours=72+1),]

    return [ Activity(facility_id=facility_ids[0], activity_type_id=activity_type_ids[i],
                      start_time=start_times[0], end_time=end_times[i])
             for i in range(len(activity_type_ids)) ]


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

    scustomer_obj = Customer(title="Mr", password="passw0rD", first_name="Standard",
                             last_name="Person", email="standard@thevertex.com", tel_number="01685469958",
                             dob=datetime.datetime(1960, 1, 1), postal_code="W1A 0AX",
                             address="3 Clos Waun Wen, Morriston", country="GB",
                             current_membership_id=1)
    pcustomer_obj = Customer(title="Lord", password="passw0rD", first_name="Premium",
                             last_name="Person", email="premium@thevertex.com", tel_number="01685469958",
                             dob=datetime.datetime(1900, 1, 1), postal_code="W1A 0AX",
                             address="3 Clos Waun Wen, Morriston", country="GB",
                             current_membership_id=2)
    return [customer_obj], [employee_obj], [manager_obj], [scustomer_obj, pcustomer_obj]


def create_customer_with_membership():

    sreceipt_obj = Receipt(customer_id=2, total_cost=3, creation_time=datetime.datetime.now())
    preceipt_obj = Receipt(customer_id=3, total_cost=10, creation_time=datetime.datetime.now())

    smembership_obj = Membership(membership_type_id=1,
                                 start_date=datetime.date.today() - datetime.timedelta(days=1),
                                 end_date=datetime.date.today() + datetime.timedelta(days=30-1),
                                 receipt_id=1)
    pmembership_obj = Membership(membership_type_id=2,
                                 start_date=datetime.date.today() - datetime.timedelta(days=1),
                                 end_date=datetime.date.today() + datetime.timedelta(days=30-1),
                                 receipt_id=2)

    return [smembership_obj, pmembership_obj], [sreceipt_obj, preceipt_obj]


def create_all():
    global facility_objs, membership_type_objs, activity_type_objs, activity_objs
    global customer_objs, customer_with_membership_objs, membership_objs, receipt_for_membership_objs
    global employee_objs, manager_objs

    facility_objs = create_facilities()
    membership_type_objs = create_membership_types()
    activity_type_objs = create_activity_types()
    activity_objs = create_activities()
    customer_objs, employee_objs, manager_objs, customer_with_membership_objs = create_users()
    membership_objs, receipt_for_membership_objs = create_customer_with_membership()
