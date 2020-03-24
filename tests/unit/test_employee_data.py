import random

from main.data.db_classes.employee_data_db_class import Employee_Router, Role


def test_employee_router_legal():
    for i in range(500):
        emp_id = random.randint(0, 10000)
        act_id = random.randint(0, 10000)
        role_id = random.randint(0, 10000)
        employee_router = Employee_Router(employee_id=emp_id, activity_id=act_id, role_id=role_id)
        assert employee_router.employee_id == emp_id
        assert employee_router.activity_id == act_id
        assert employee_router.role_id == role_id


def test_role_legal():
    names = ["Lifeguard", "ALLCAPS"]
    descriptions = ["Lorem ipsum",
                    "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()_+-=[]{};':,./<>?\"/*-+`~"]

    # Change expected result as implementation decision changes, but the tests should still pass after those changes
    exp_names = ["lifeguard", "allcaps"]
    exp_descriptions = ["Lorem ipsum",
                    "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()_+-=[]{};':,./<>?\"/*-+`~"]
    for i in range(10):
        role = Role(role_name=names[i % 2], description=descriptions[i % 2], hourly_pay=pow(2, i))
        assert role.role_name == exp_names[i % 2]
        assert role.description == exp_descriptions[i % 2]
        assert role.hourly_pay == pow(2, i)
