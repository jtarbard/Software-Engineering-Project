

"""
<Rule '/account/register' (OPTIONS, HEAD, GET) -> account.register_get>
<Rule '/account/register' (OPTIONS, POST) -> account.register_post>
<Rule '/account/log_out' (OPTIONS, HEAD, GET) -> account.log_out>
<Rule '/account/login' (OPTIONS, HEAD, GET) -> account.login_get>
<Rule '/account/login' (OPTIONS, POST) -> account.login_post>
"""


def test_register(test_client):
    assert False


def test_login(test_client):
    assert False


def test_logout(test_client):
    assert False