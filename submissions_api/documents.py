from datetime import datetime

from submissions_api import db


class Study(db.Document):
    name = db.StringField(required=True)
    available_places = db.IntField(required=True)
    user = db.StringField(required=True)

    meta = {
        'indexes': [
            {
                'fields': ['name'],
                'unique': True
            },
            {
                'fields': ['user'],
                'unique': False
            }
        ]
    }


class Submission(db.Document):
    study = db.ReferenceField('Study', required=True)
    user = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.now())

    meta = {
        'indexes': [
            {
                'fields': ['study', 'user'],
                'unique': True
            }
        ]
    }
