from bs4 import BeautifulSoup


def test_about_get(test_client, page_title_dict):
    """
    GIVEN a Flask application
    WHEN the '/info/about' page is requested (GET)
    THEN check the response is valid

    TESTING FOR <Rule '/info/about' (OPTIONS, HEAD, GET) -> info.about_view>
    """
    response = test_client.get("/info/about")

    soup = BeautifulSoup(response.data, 'html.parser')

    assert response.status_code == 200
    assert soup.title.string.strip() == page_title_dict["about.html"].strip()  # for simple pages, this suffices
