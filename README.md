# plaid-integration

Plaid integration app exposes rest end points for fetching details about the users accounts and transactions.

## Setup

Clone the repository : `git clone https://github.com/vineet-bhikonde/plaid-integration`

`cd plaid-integration`

Creating the virtual environment : `python3 -m venv plaid-env`

Activate virtual environment : `source plaid-env/bin/activate`

Deactivate virtual environment : `deactivate`

Installing the dependencies : `pip install -r requirements.txt`

Starting the server : `python manage.py runserver`


##Endpoints

**User**

api/v1/user/register/ POST - registering new user

api/v1/user/login/ POST - logging in a user

api/v1/user/logout POST - logout a user


**Item**

api/v1/item/access-token POST - fetching access token from public token

api/v1/item/accounts - GET - fetching user account details

api/v1/item/transactions - GET - fetching user transactions

api/v1/item/transactions - POST - fetching user transactions from plaid


**Webhook**

api/v1/item/webhook/transactions - POST - webhook for transactions

api/v1/item/webhook/transactions/fire - GET - fire webhook for testing

api/v1/item/webhook/register - POST - register webhook for first item of user