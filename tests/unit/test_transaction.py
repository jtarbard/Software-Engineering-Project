from main.data.db_classes.transaction_db_class import Receipt, PaymentDetails, MembershipType, Membership, Booking
import random
import datetime


def test_receipt_legal():
    for i in range(500):
        id = random.randint(0, 10000)
        cost = round(random.random() * random.randint(0, 10000), random.randint(0, 10))
        receipt = Receipt(customer_id=id, total_cost=cost)
        assert receipt.customer_id == id
        assert receipt.total_cost == cost


def test_booking_legal():
    for i in range(500):
        act_id = random.randint(0, 10000)
        receipt_id = random.randint(0, 10000)
        booking = Booking(activity_id=act_id, receipt_id=receipt_id)
        assert booking.activity_id == act_id
        assert booking.receipt_id == receipt_id


def test_membership_legal():
    for i in range(500):
        type_id = random.randint(0, 10)
        start_date = datetime.date.today() - datetime.timedelta(days=random.randint(0, 10000))
        end_date = start_date + datetime.timedelta(days=random.randint(0, 10000))
        receipt_id = random.randint(0, 10000)
        membership = Membership(membership_type_id=type_id, start_date=start_date, end_date=end_date,
                                receipt_id=receipt_id)
        assert membership.membership_type_id == type_id
        assert membership.start_date == start_date
        assert membership.end_date == end_date
        assert membership.receipt_id == receipt_id


def test_membership_type_legal():
    names = ["Standard", "Premium"]
    descriptions = ["Lorem ipsum",
                   "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()_+-=[]{};':,./<>?\"/*-+`~"]
    discounts = [0, 100]
    monthly_prices = [0, 100]

    # Change expected result as implementation decision changes, but the tests should still pass after those changes
    exp_names = ["Standard", "Premium"]
    exp_descriptions = ["Lorem ipsum",
                        "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()_+-=[]{};':,./<>?\"/*-+`~"]
    exp_discounts = [0, 100]
    exp_monthly_prices = [0, 100]
    for i in range(len(names)):
        m_type = MembershipType(name=names[i], description=descriptions[i], discount=discounts[i],
                                monthly_price=monthly_prices[i])
        assert m_type.name == exp_names[i]
        assert m_type.description == exp_descriptions[i]
        assert m_type.discount == exp_discounts[i]
        assert m_type.monthly_price == exp_monthly_prices[i]


def test_payment_details_legal():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    future = today + datetime.timedelta(days=365)

    card_nums = ["0000 0000 0000 0000", "9999 9999 9999 9999", "0123 4567 8901 2345"]
    start_dates = ["01/01", str(today.day)+"/"+str(today.month), "03/17"]
    expir_dates = [str(tomorrow.day)+"/"+str(tomorrow.month), str(future.day)+"/"+str(future.month), "09/22"]
    street_and_numbers = ["Rake Hill, Primrose Lane, Liss", "37 Bradford Street, Market Harborough", "15 Sandiway, Glossop"]
    towns = ["some town", "CAPITAL TOWN", "idk"]
    cities = ["Liss", "Market Harborough", "Glossop"]
    postcodes = ["GU33 7PL", "LE16 9FJ", "SK13 8SS"]

    # Change expected result as implementation decision changes, but the tests should still pass after those changes
    exp_card_nums = ["0000 0000 0000 0000", "9999 9999 9999 9999", "0123 4567 8901 2345"]
    exp_start_dates = ["01/01", str(today.day)+"/"+str(today.month), "03/17"]
    exp_expir_dates = [str(tomorrow.day)+"/"+str(tomorrow.month), str(future.day)+"/"+str(future.month), "09/22"]
    exp_street_and_numbers = ["Rake Hill, Primrose Lane, Liss", "37 Bradford Street, Market Harborough", "15 Sandiway, Glossop"]
    exp_towns = ["some town", "CAPITAL TOWN", "idk"]
    exp_cities = ["Liss", "Market Harborough", "Glossop"]
    exp_postcodes = ["GU33 7PL", "LE16 9FJ", "SK13 8SS"]
    for i in range(len(card_nums)):
        payment_detail = PaymentDetails(card_number=card_nums[i], start_date=start_dates[i],
                                        expiration_date=expir_dates[i],
                                        street_and_number=street_and_numbers[i], town=towns[i], city=cities[i],
                                        postcode=postcodes[i])
    assert payment_detail.card_number == exp_card_nums[i]
    assert payment_detail.start_date == exp_start_dates[i]
    assert payment_detail.expiration_date == exp_expir_dates[i]
    assert payment_detail.street_and_number == exp_street_and_numbers[i]
    assert payment_detail.town == exp_towns[i]
    assert payment_detail.city == exp_cities[i]
    assert payment_detail.postcode == exp_postcodes[i]
