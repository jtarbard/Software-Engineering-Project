import random
import datetime

from main.data.db_classes.activity_db_class import Activity, SessionType, Facility, FacilityType


def test_activity_type_legal():
    names = ["Basketball", "ALLCAPS"]
    descriptions = ["Lorem Ipsum",
                    "1234567890!@#$%^&*()-=_+qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM`~[]{}\\|;':\",./<>?"]
    categories = ["Category", "ALLCAPS"]
    tagss = ["tag1:tag2:tag3", "TAG1:taG2:tAG3:tag4:&*(:end"]

    # Change expected result as implementation decision changes, but the tests should still pass after those changes
    exp_names = ["basketball", "allcaps"]
    exp_descriptions = ["Lorem Ipsum",
                    "1234567890!@#$%^&*()-=_+qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM`~[]{}\\|;':\",./<>?"]
    exp_categories = ["Category", "ALLCAPS"]
    exp_tagss = ["tag1:tag2:tag3", "TAG1:taG2:tAG3:tag4:&*(:end"]

    for i in range(500):
        index = i % len(names)

        min_age = random.randint(3, 100)
        max_cap = random.randint(3, 1000)
        hourly_cost = random.randint(3, 100)
        hourly_price = hourly_cost + random.randint(3, 100)
        min_staff = random.randint(3, 100)
        max_staff = min_staff + random.randint(3, 100)
        act_type = SessionType(name=names[index], description=descriptions[index],
                               category=categories[index], tags=tagss[index],
                               minimum_age=min_age, maximum_activity_capacity=max_cap,
                               hourly_activity_cost=hourly_cost,
                               hourly_activity_price=hourly_price,
                               max_staff=max_staff, min_staff=min_staff)
        assert act_type.name == exp_names[index]
        assert act_type.description == exp_descriptions[index]
        assert act_type.category == exp_categories[index]
        assert act_type.tags == exp_tagss[index]
        assert act_type.minimum_age == min_age
        assert act_type.maximum_activity_capacity == max_cap
        assert act_type.hourly_activity_cost == hourly_cost
        assert act_type.hourly_activity_price == hourly_price
        assert act_type.max_staff == max_staff
        assert act_type.min_staff == min_staff


def test_activity_legal():
    for i in range(500):
        fac_id = random.randint(0, 10000)
        act_id = random.randint(0, 10000)
        start_time = datetime.date.today() - datetime.timedelta(days=random.randint(0, 10000))
        end_time = start_time + datetime.timedelta(days=random.randint(0, 10000))
        activity = Activity(facility_id=fac_id, activity_type_id=act_id,
                            start_time=start_time, end_time=end_time)
        assert activity.facility_id == fac_id
        assert activity.activity_type_id == act_id
        assert activity.start_time == start_time
        assert activity.end_time == end_time


def test_facility_type_legal():
    names = ["Basketball Court Type", "ALLCAPS"]
    descriptions = ["Lorem Ipsum",
                    "1234567890!@#$%^&*()-=_+qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM`~[]{}\\|;':\",./<>?"]

    # Change expected result as implementation decision changes, but the tests should still pass after those changes
    exp_names = ["basketball court", "allcaps"]
    exp_descriptions = ["Lorem Ipsum",
                        "1234567890!@#$%^&*()-=_+qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM`~[]{}\\|;':\",./<>?"]

    for i in range(500):
        index = i % len(names)

        max_cap = random.randint(3, 1000)
        facility_type = FacilityType(facility_type_name=names[index], description=descriptions[index], max_capacity=max_cap)

        assert facility_type.facility_type_name == exp_names[index]
        assert facility_type.description == exp_descriptions[index]
        assert facility_type.max_capacity == max_cap


def test_facility_legal():
    names = ["Basketball Court", "ALLCAPS"]

    # Change expected result as implementation decision changes, but the tests should still pass after those changes
    exp_names = ["basketball court", "allcaps"]

    for i in range(500):
        index = i % len(names)

        facility = Facility(name=names[index], facility_type_id=i)

        assert facility.name == exp_names[index]
        assert facility.facility_type_id == i

