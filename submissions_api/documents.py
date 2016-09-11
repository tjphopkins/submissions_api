from datetime import datetime
from mongoengine import ValidationError

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

    def validate(self, clean=True):
        # TODO: Not keen on doing this db lookup on each save.
        print "study", self.study.id
        if Submission.objects.filter(
                study=self.study).count() >= self.study.available_places:
            raise ValidationError(
                "A maximum of {study.available_places} submissions allowed for"
                " the {study.name}".format(study=self.study))

        super(Submission, self).validate()
