# Dela (pronounced "D" "ela", swedish word for "share")

Message sharing system with the following features:

* Client can create a message, and get the URL to the message.
* Client can view any message, if the URL is known to the client.
* It should be infeasible to guess the URL to a message.
* Messages should only be stored and available on the server for 7 days, and deleted automatically thereafter.

## Design Notes

The following considerations were implemented:

* An in-memory solution is used to store data for this service considering appropriate HTTP verbs, headers and responses as applicable.
* Unit Tests were implemented to assert correctness of system functionality.
* Security risks/assumptions are documented (see below)

## Security Risks/Assumptions

 
