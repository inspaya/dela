[![Ceasefire Now](https://badge.techforpalestine.org/ceasefire-now)](https://techforpalestine.org/learn-more)

[![inspaya](https://circleci.com/gh/inspaya/dela.svg?style=svg)](https://app.circleci.com/pipelines/github/inspaya/dela)

# Dela (pronounced "D" "ela", swedish word for "share")

Message sharing system with the following features:

* Client can create a message, and get the URL to the message.
* Client can view any message, if the URL is known to the client.
* It should be infeasible to guess the URL to a message.
* Messages should only be stored and available on the server for 7 days, and deleted automatically thereafter.

## Project Setup

This project can be setup using any of the following techniques:

* Manually
  1. Clone this repo
  2. Create a Python3 virtual environment in the project folder
  3. Install the project requirements
  4. Run the app and issue requests.
  5. Optionally run the tests
  ```shell
  $ git clone https://github.com/inspaya/dela.git
  $ cd dela
  $ python3 -m venv .
  $ source bin/activate
  $ pip install -r requirements.txt
  $ flask run
  $ # To add a message, execute
  $ curl -X POST 'http://127.0.0.1:5000/messages/new' \
  --header 'Content-Type: application/json' \
  --data-raw '{"message":"What a beautiful day"}'
  $ # To view a message, execute
  $ curl http://127.0.0.1:5000/messages/view/<ID_RETURNED_FROM_THE_POST_REQUEST>
  $ # To run tests, execute
  $ pytest test_app.py
  $ # .. or if you want to see test coverage reports, execute
  $ coverage run app.py && coverage report app.py
  ```
* Using Docker
  1. Clone this repo
  2. Build the docker image
  3. Run a container and issue requests.
  4. Optionally run the tests
  ```shell
  $ git clone https://github.com/inspaya/dela.git
  $ cd dela
  $ docker build -t inspaya-dela .
  $ docker run -p 5000:5000 --name dela -it --rm --init inspaya-dela
  $ # To add a message, execute
  $ curl -X POST 'http://127.0.0.1:5000/messages/new' \
  --header 'Content-Type: application/json' \
  --data-raw '{"message":"What a beautiful day"}'
  $ # To view a message, execute
  $ curl http://127.0.0.1:5000/messages/view/<ID_RETURNED_FROM_THE_POST_REQUEST>
  $ # To run tests, execute
  $ docker exec -it <insert_container_id_here> pytest test_app.py
  $ # Generate Unit Test Coverage for the app.py script
  $ docker exec -it <insert_container_id_here> coverage run app.py
  $ docker exec -it <insert_container_id_here> coverage report app.py
  ```

## Design Notes

The following considerations were implemented:

* An in-memory solution is used to store data for this service considering appropriate HTTP verbs, headers and responses as applicable.
* Unit Tests were implemented to assert correctness of system functionality.
* Security risks/assumptions are documented (see below)

## Security Risks/Assumptions

The following risks and assumptions were considered:

* This service receives data from any client in the JSON format below. Please note the `message` key is required. No additional inspection is done on the value of the `message` provided and HTML-escaping is done when viewing the content.
  ```json
  {
     "message": "What a beautiful day"
  }
  ```
* Defaults provided, which can be changed by environment variables, include:
  * Size of in-memory solution ( i.e. `cache`) used is 1000 items. This can be changed by setting the `CACHE_MAX_LEN` environment variable.
  * Time-To-Live (TTL) for items stored is currently 7 days. This can be changed by setting the `CACHE_MAX_AGE_SECS` environment variable.
  * A Request/Response rate-limit of 3 requests per minute is set. This can be changed by setting the `DEFAULT_RATE_LIMIT` environment variable or per endpoint as demonstrated for the `/messages/new` endpoint.
