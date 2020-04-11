import pytest


def pytest_generate_tests(metafunc):
    generic_test_ids = ["[Basic] Not logged in, No membership",
                        "[Basic] Logged in, No membership",
                        "[Basic] Logged in, standard membership",
                        "[Basic] Logged in, premium membership",
                        "[Extra] Basket cookie is retained and unmodified"]

    if "view_activity_types_get_data" in metafunc.fixturenames:
        metafunc.parametrize("view_activity_types_get_data", range(5), indirect=True,
                             ids=generic_test_ids)


@pytest.fixture
def view_activity_types_get_data(request, generic_route_data):
    """
    About_Get_Test (Generic Page) TODO: Maybe check google map works?
    GIVEN a Flask application
    WHEN the '/activities/types' page is requested (GET)
    VARYING CONDITIONS 1. User with/without membership is logged in / not logged in
    THEN check 1. Valid status code (200)
               2. The redirected url
               3. page_title (rendered template parameter) or actual page title
               4. name of the rendered template
               5. Existing cookies

    TESTING FOR <Rule '/activities/types' (OPTIONS, POST, HEAD, GET) -> activities.view_classes_types>
    """

    return generic_route_data(request=request,
                              exp_title="Activities",
                              exp_url="/activities/types",
                              exp_template_path="/activities/activity_types.html",
                              needs_login=False)
