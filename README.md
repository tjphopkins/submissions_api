# Studies and submissions Flask API

## Install

pip install -r requirements.txt

## Run

From the top-level submissions_api directory, run 'python runserver.py'.
Notw the localhost port on which the Flask dev server is running printed to the
terminal.

## Use Cases

* List all studies:
`curl http://localhost:5000/studies`

* List all studies for a given user:
`curl http://localhost:5000/studies?user=user_id`

* Create new study:
`curl --data "name=study_name&available_places=30&user=user_id" http://localhost:5000/studies`

* List all submissions by user:
`curl http://localhost:5000/submissions?user=user_id`

* Create new submission
`curl --data "study=:study_id&user:user_id" http://localhost:5000/submissions`
