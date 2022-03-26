from os import environ
from secrets import token_hex

from expiringdict import ExpiringDict
from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from markupsafe import escape

CACHE_MAX_LEN = environ.get('CACHE_MAX_LEN') or 1000
CACHE_MAX_AGE_SECS = environ.get('CACHE_MAX_AGE_SECS') or 604800
DEFAULT_RATE_LIMIT = environ.get('DEFAULT_RATE_LIMIT') or "3/minute"  # we use this as a minimum value

app = Flask(__name__)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[DEFAULT_RATE_LIMIT]
)


def _create_cache(cache_max_len=CACHE_MAX_LEN, cache_max_age=CACHE_MAX_AGE_SECS):
    return ExpiringDict(max_len=cache_max_len, max_age_seconds=cache_max_age)


def _create_and_store_message(message):
    message_id = token_hex()
    cache[message_id] = message
    return message_id


def _get_message_by_id(message_id):
    if message_id in cache.keys():
        return cache.get(message_id), 200
    return f"Message with id {message_id} not found", 404


cache = _create_cache()


@app.errorhandler(429)
def rate_limit_exceeded(e):
    return f"Sorry, you have exceeded your {e.description} rate limit.", 429


@app.route("/messages/new", methods=['POST'])
@limiter.limit("5/minute", override_defaults=True)
def create_message():
    request_data = request.get_json()
    if 'message' in request_data.keys():
        message = request_data.get('message')
        message_id = _create_and_store_message(message)
        message_url = f"{request.host_url}messages/view/{message_id}"
        return f"New message created. Available at {message_url}\n", 201
    return f"Please provide a message to be created", 400


@app.route("/messages/view/<message_id>", methods=['GET'])
def view_message(message_id):
    message, status_code = _get_message_by_id(message_id)
    return f"{escape(message)}", status_code
