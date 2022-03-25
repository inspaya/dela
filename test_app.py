import pytest

from app import app as flask_app, cache, _create_and_store_message


@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client


def test_create_message_succeeds_and_returns_http_201(client):
    """
    GIVEN a request with a json payload containing a "message" key
    WHEN the '/messages/new' endpoint is POSTed to
    THEN check that a valid URL is returned
    """
    response = client.post(
        path="/messages/new", json={"message": "Some random message"}
    )

    assert response.status_code == 201
    assert "New message created. Available at" in response.get_data(True)


def test__create_and_store_message(client):
    """
    GIVEN a message
    WHEN the _create_and_store_message() function is called with that 'message'
    THEN check that the message has been created and stored
    """
    message_text = "Message to test creating and storing"
    message_id = _create_and_store_message(message_text)
    message_ids_matched = []
    for unique_id, message in cache.items():
        if message_text == message:
            message_ids_matched.append(unique_id)

    assert message_id in message_ids_matched


def test__create_and_store_message_enforces_unique_urls(client):
    """
    GIVEN two or more similar messages
    WHEN the _create_and_store_message() function is called with each 'message' separately
    THEN check that a unique id (which is part of the URL) is created and stored for each message
    """
    message_text1 = "Message to test creating and storing with unique ids"
    message_text2 = "Message to test creating and storing with unique ids"
    message_text3 = "Message to test creating and storing with unique ids"

    message_id1 = _create_and_store_message(message_text1)
    message_id2 = _create_and_store_message(message_text2)
    message_id3 = _create_and_store_message(message_text3)

    message_ids_matched = []
    for unique_id, message in cache.items():
        if message_text1 == message or message_text2 == message or message_text3 == message:
            message_ids_matched.append(unique_id)

    assert message_id1 in message_ids_matched
    assert message_id2 in message_ids_matched
    assert message_id3 in message_ids_matched

    assert message_ids_matched == list(set(message_ids_matched))
