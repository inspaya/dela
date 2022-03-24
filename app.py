from secrets import token_hex
from flask import Flask, request
from expiringdict import ExpiringDict

app = Flask(__name__)
cache = ExpiringDict(max_len=1000, max_age_seconds=604800)


@app.route("/messages/new", methods=['POST'])
def create_message():
    request_data = request.get_json()
    if 'message' in request_data.keys():
        message = request_data.get('message')
        message_id = _create_and_store_message(message)
        message_url = f"{request.host_url}messages/view/{message_id}"
        return f"New message created. Available at {message_url}", 201
    return f"Please provide a message to be created", 400


@app.route("/messages/view/<message_id>", methods=['GET'])
def view_message(message_id):
    message = _get_message_by_id(message_id)
    return f"{message}"


def _create_and_store_message(message):
    message_id = token_hex()
    cache[message_id] = message
    return message_id


def _get_message_by_id(message_id):
    if message_id in cache.keys():
        return cache.get(message_id)
    return f"Message with id {message_id} not found"
