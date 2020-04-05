import datetime


def test_new_customer_legal():
    """
    GIVEN a Customer object
    WHEN a new Customer is created
    THEN check all fields are defined correctly
    """
    from tests.helper.database_creation import customer_objs, employee_objs, manager_objs

    objs = [customer_objs[0], employee_objs[0], manager_objs[0]]

    exp_titles = ["mr", "mr", "mrs"]
    exp_passwords = ["passw0rD", "oai9*(13jiovn__eiqf9OIJqlk", "Admin666"]
    exp_first_names = ["John", "FIRSTNAME", "jane"]
    exp_last_names = ["doe", "lastname", "doe"]
    exp_emails = ["johndoe@thevertex.com", "notsurewhattoexpect@but.hereyougo", "JANEDOE@GMAIL.COM"]
    exp_tels = ["01685469958", "13854685599", "99999999999"]
    exp_bdays = [datetime.datetime(1960, 1, 1), datetime.datetime(1975, 1, 4), datetime.datetime(2004, 3, 22)]
    exp_postcodes = ["W1A 0AX", "DN55 1PT", "EC1A 1BB"]
    exp_addresses = ["3 clos waun wen, morriston", "the old mill, llwyngwril", "14 gwyn drive, caerphilly"]
    exp_countries = ["gb", "us", "cn"]

    for i in range(3):
        user = objs[i]
        assert user.title == exp_titles[i]
        assert not user.password == exp_passwords[i]
        assert user.password_match(exp_passwords[i])
        assert user.first_name == exp_first_names[i]
        assert user.last_name == exp_last_names[i]
        assert user.email == exp_emails[i]
        assert user.tel_number == exp_tels[i]
        assert user.dob == exp_bdays[i]
        assert user.postal_code == exp_postcodes[i]
        assert user.address == exp_addresses[i]
        assert user.country == exp_countries[i]


