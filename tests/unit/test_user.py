import datetime


def test_new_customer_legal(new_user):
    """
    GIVEN a Customer object
    WHEN a new Customer is created
    THEN check all fields are defined correctly
    """
    types = ["customer", "manager", "employee"]

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

    users = []
    for i in range(3):
        users.append(new_user(types[i], title=titles[i], password=passwords[i], first_name=first_names[i],
                              last_name=last_names[i], email=emails[i], tel_number=tels[i],
                              dob=bdays[i], postal_code=postcodes[i], address=addresses[i], country=countries[i]))
        assert users[i].title == exp_titles[i]
        assert not users[i].password == exp_passwords[i]
        assert users[i].password_match(passwords[i])
        assert users[i].first_name == exp_first_names[i]
        assert users[i].last_name == exp_last_names[i]
        assert users[i].email == exp_emails[i]
        assert users[i].tel_number == exp_tels[i]
        assert users[i].dob == exp_bdays[i]
        assert users[i].postal_code == exp_postcodes[i]
        assert users[i].address == exp_addresses[i]
        assert users[i].country == exp_countries[i]


