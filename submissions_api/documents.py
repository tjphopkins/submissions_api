from datetime import datetime
from mongoengine import ValidationError, NotUniqueError
from bson import ObjectId

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


def _get_study_submissions_count(study):
    return len(Submission.objects.filter(study=study))


class Submission(db.Document):
    study = db.ReferenceField('Study', required=True)
    user = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.now())
    study_submission_number = db.IntField()

    meta = {
        'indexes': [
            {
                'fields': ['study', 'user'],
                'unique': True
            },
            {
                'fields': ['user'],
                'unique': False
            },
            # Not allowing duplicate submission numbers per study will act
            # as concurrency control for submission creation. See validate
            # method for more info.
            {
                'fields': ['study', 'study_submission_number'],
                'unique': True
            }
        ]
    }

    @staticmethod
    def create_new(study_id, user_id):
        """Creates a new submission object

        :arg study_id str: id of study for which to create submission
        :arg user_id str: id of user for which to create submission
        :return submission object
        """
        try:
            study = Study.objects.get(id=ObjectId(study_id))
            submission = Submission(study=study, user=user_id)
            submission.study_submission_number = \
                _get_study_submissions_count(study)
            submission.save()
        except (NotUniqueError, ValidationError) as e:

            # If attempting to save submission with duplicated
            # study_submission_number, retry
            if isinstance(e, NotUniqueError) and \
                    'study_submission_number' in str(e):
                submission = Submission.create_new(study_id, user_id)
                return submission
            raise
        else:
            return submission

    def save(self):
        """Performs validation on number of available places on study before
        persisting to database.
        """
        if self.study_submission_number >= self.study.available_places:
            raise ValidationError(
                "A maximum of {study.available_places} submissions allowed for"
                " the {study.name}".format(study=self.study))

        # Consider two requests, both attempting to the save a submission for
        # the same study, passing the avaialble_places check concurrently. Both
        # will attempt to save the Submission with the same
        # study_submission_number. Only one will save successfully whilst the
        # other will raise a NotUniqueError and retry.
        super(Submission, self).save()
