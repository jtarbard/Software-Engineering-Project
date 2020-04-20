import pytest


def pytest_generate_tests(metafunc):
    generic_test_ids = ["[Basic] Not logged in, No membership",
                        "[Basic] Logged in, No membership",
                        "[Basic] Logged in, standard membership",
                        "[Basic] Logged in, premium membership",
                        "[Extra] Basket cookie is retained and unmodified"]

    if "index_func_data" in metafunc.fixturenames:
        metafunc.parametrize("index_func_data", range(5), indirect=True,
                             ids=generic_test_ids)


@pytest.fixture
def index_func_data(request, generic_route_data):
    """
    About_Get_Test (Generic Page) TODO: Maybe check google map works?
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    VARYING CONDITIONS 1. User with/without membership is logged in / not logged in
    THEN check 1. Valid status code (200)
               2. The redirected url
               3. page_title (rendered template parameter) or actual page title
               4. name of the rendered template
               5. Existing cookies

    TESTING FOR <Rule '/' (OPTIONS, HEAD, GET) -> index.index_func>
    """

    return generic_route_data(request=request,
                              exp_title="Index",
                              exp_url="/",
                              exp_template_path="/index/index.html")
