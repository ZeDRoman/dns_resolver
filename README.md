**DNS resolver with cache**

Realization of recursive dns resolver that can request authoritative DNS servers starting from root server.
Resolver uses cache to save ip known hostnames for limited TTL

Interaction with resolver is realized using flask webserver.

*API*:
    get-a-records?domain=[DOMAIN_NAME_HERE]&trace=[true/false]

*RUN*:
    Start run.py using python3

*EXAMPLE*:

1. REQUEST:
    curl "localhost:5000/get-a-records?domain=ya.ru&trace=true"

RESPONSE:
    {
      "address": "87.250.250.242",
      "domain": "ya.ru",
      "trace": [
        "193.0.14.129",
        "193.232.128.6",
        "213.180.193.1"
       ]
    }


2. REQUEST:
    curl "localhost:5000/get-a-records?domain=google.com"

RESPONSE:
    {
      "address": "64.233.161.102",
      "domain": "google.com"
    }

