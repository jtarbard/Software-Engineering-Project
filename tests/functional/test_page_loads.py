def test_homepage(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"The Vertex-Index!" in response.data
    assert b"The Vertex Gym" in response.data
    assert b"Join Now" in response.data
    # TOOD: assert nav bar items


def test_memberships(test_client):
    """
    GIVEN a Flask application
    WHEN the '/info/memberships' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/info/memberships')
    assert response.status_code == 200
    assert b"The Vertex memberships!" in response.data
    assert b"Standard Membership" in response.data
    assert b"Premium Membership" in response.data
    # TOOD: assert nav bar items