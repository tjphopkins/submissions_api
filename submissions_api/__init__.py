"""Flask Studies and Submissions application"""

from flask import Flask
from flask_mongoengine import MongoEngine


app = Flask(__name__)
db = MongoEngine(app)
app.config.update(
    SECRET_KEY="developmentkey",
    MONGODB_SETTINGS={'DB': "submissions"},
    DATABASE=db
)


if __name__ == '__main__':
    app.run(debug=True)
