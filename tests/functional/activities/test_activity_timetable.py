

"""
<Rule '/activities/view_activities' (OPTIONS, POST, HEAD, GET) -> activities.view_classes>
<Rule '/activities/view_activity/<activity_id>' (OPTIONS, HEAD, GET) -> activities.view_class>
<Rule '/activities/<sent_activity>_<multiple>' (OPTIONS, POST, HEAD, GET) -> activities.view_classes>
"""


def test_view_activities():
    assert False


def test_view_activity_individual():
    assert False


# def test_view_sent_activity_multiple():
#     assert False
