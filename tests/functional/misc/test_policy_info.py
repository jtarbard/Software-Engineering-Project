from bs4 import BeautifulSoup


def test_policy_info_get(test_client, page_title_dict):
    """
    GIVEN a Flask application
    WHEN the '/misc/policy_info' page is requested (GET)
    THEN check the response is valid

    TESTING FOR <Rule '/misc/policy_info' (OPTIONS, HEAD, GET) -> misc.policy_info_view>
    """
    response = test_client.get("/misc/policy_info")

    soup = BeautifulSoup(response.data, 'html.parser')

    assert response.status_code == 200
    assert soup.title.string.strip() == page_title_dict["policy_info.html"].strip()  # for simple pages, this suffices
