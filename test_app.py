import pytest
from os import environ
from time import sleep
from unittest.mock import Mock, patch
from expiringdict import ExpiringDict
from app import app as flask_app, cache, _create_and_store_message, \
    _create_cache, _get_message_by_id, limiter, CACHE_MAX_LEN, CACHE_MAX_AGE_SECS, DEFAULT_RATE_LIMIT
from markupsafe import escape


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


def test_create_message_fails_and_returns_http_400_for_a_bad_payload(client):
    """
    GIVEN a request with a json payload missing the "message" key
    WHEN the '/messages/new' endpoint is POSTed to
    THEN check that an error message is returned along with HTTP 400
    """
    response = client.post(
        path="/messages/new", json={"problem": "I don't have a message key"}
    )

    assert response.status_code == 400
    assert response.get_data(True) == "Please provide a message to be created"


def test_create_cache_works_correctly():
    """
    GIVEN a set of config parameters for initializing an ExpiringDict cache
    WHEN the app is run for the first time
    THEN check that an in-memory cache was created with the right properties
    """
    cache_created = _create_cache()
    assert type(cache_created) is ExpiringDict
    assert cache_created.max_age == CACHE_MAX_AGE_SECS
    assert cache_created.max_len == CACHE_MAX_LEN


def test_get_message_by_id_returns_messages_for_valid_ids():
    """
    GIVEN an id
    WHEN the in-memory cache is queried for this id
    THEN the associated message should be returned
    """
    message_text = "Message to test retrieving valid ids"
    message_id = _create_and_store_message(message_text)
    message, response_code = _get_message_by_id(message_id)

    assert message == message_text
    assert response_code == 200


def test_get_message_by_id_returns_errors_for_invalid_ids():
    """
    GIVEN an in-existent id
    WHEN the in-memory cache is queried for this id
    THEN an error message should be returned
    """
    message_id = "Some_fake_id_that_never_got_created"
    message, response_code = _get_message_by_id(message_id)

    assert message == f"Message with id {message_id} not found"
    assert response_code == 404


def test_get_message_by_id_escapes_html_content(client):
    """
    GIVEN a valid id referencing HTML message content
    WHEN the in-memory cache is queried for this id
    THEN check that the HTML message content is escaped before display
    """
    message_text = "<script>alert('Busted!')</script>"
    post_response = client.post(
        path="/messages/new", json={"message": message_text}
    )

    message_id = post_response.get_data(True).split('messages/view/')[1]
    get_response = client.get(path=f"/messages/view/{message_id}")

    assert f"{escape(message_text)}" == get_response.get_data(True)
    assert get_response.status_code == 200


def test_create_and_store_message():
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


def test_create_and_store_message_enforces_unique_urls():
    """
    GIVEN two or more similar messages
    WHEN the _create_and_store_message() function is called with each 'message' separately
    THEN check that a unique id (which is part of the URL) is created and stored for each message
    """
    dipo = "End game"
    sophie = "End game"
    moyin = "End game"

    message_id1 = _create_and_store_message(dipo)
    message_id2 = _create_and_store_message(sophie)
    message_id3 = _create_and_store_message(moyin)

    message_ids_matched = []
    for unique_id, message in cache.items():
        if dipo == message or sophie == message or moyin == message:
            message_ids_matched.append(unique_id)

    assert message_id1 in message_ids_matched
    assert message_id2 in message_ids_matched
    assert message_id3 in message_ids_matched

    assert sorted(message_ids_matched) == sorted(list(set(message_ids_matched)))


def test_request_rate_limit_is_honored_for_creating_new_messages(client):
    """
    GIVEN a set of requests
    WHEN the '/messages/new' endpoint is POSTed to
    THEN check that the stated rate-limit is respected after valid number of requests is made
    """
    data_fixture = range(1, 1000)
    response = None
    for data in data_fixture:
        response = client.post(
            path="/messages/new", json={"message": data}
        )

    current_limit = limiter.current_limit
    route_request_limit_message = str(current_limit.limit)

    assert response.status_code == 429
    assert f"Sorry, you have exceeded your {route_request_limit_message} rate limit." in response.get_data(True)


def test_request_rate_limit_is_honored_for_viewing_messages(client):
    """
    GIVEN a set of requests
    WHEN the '/messages/view/<message_id>' endpoint is requested (GET)
    THEN check that the stated rate-limit is respected after valid number of requests is made
    """
    max_request_count = int(DEFAULT_RATE_LIMIT.split('/')[0])
    data_fixture = range(0, max_request_count + 1)
    message_ids = [_create_and_store_message(data) for data in data_fixture]

    response = None
    for message_id in message_ids:
        response = client.get(path=f"/messages/view/{message_id}")

    current_limit = limiter.current_limit
    route_request_limit_message = str(current_limit.limit)

    assert response.status_code == 429
    assert f"Sorry, you have exceeded your {route_request_limit_message} rate limit." in response.get_data(True)
