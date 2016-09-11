# Studies and submissions Flask API

## Get up and running:

Inside a python2 environment, pip install the following packages:
* flask
* flask-mongoengine
* mock

From the top-level submissions_api directory, run 'python runserver.py'.
The localhost port on which the Flask dev server is running will be printed.

## Use cases

* List all studies:
`curl http://localhost:5000/studies`

* List all studies for a given user:
`curl http://localhost:5000/studies?user=user_id`

* Create new study:
`curl --data "name=study_name&available_places=30&user=user_id" http://localhost:5000/studies`

* List all submissions by user:
`curl http://localhost:5000/studies?user=user_id`

* Create new submission
`curl --data "study=:study_id&user:user_id" http://localhost:5000/submissions`

**NOTE**: All endpoints will use the http protocol, not https, since the app does
not use SSL.
