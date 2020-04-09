import pytest


def pytest_generate_tests(metafunc):
    if "basket_cookie_data" in metafunc.fixturenames:
        metafunc.parametrize("basket_cookie_data", range(25), indirect=True)


@pytest.fixture
def basket_cookie_data(request):
    from main.helper_functions.test_helpers.database_creation import activity_objs, membership_type_objs

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
