"""Flask Studies and Submissions application"""

from flask import Flask
from flask_mongoengine import MongoEngine
import json

from submissions_api import api


app = Flask(__name__)
db = MongoEngine(app)
app.config.update(
    SECRET_KEY="developmentkey",
    MONGODB_SETTINGS={'DB': "submissions"},
    DATABASE=db
)


if __name__ == '__main__':
    app.run(debug=True)


# VIEWS #
# I'd usally give these their own file, but seeing as this app is small,
# I'll keep them in here.

@app.route('/')
def index():
    return "This is the index. Nothing to see here."


@app.route('/studies', methods=['GET'])
def studies():
    studies = api.get_all_studies()
    return json.dumps(studies)
