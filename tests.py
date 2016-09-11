"""Test cases for Studies and Submissions application"""

import unittest
from mock import patch
from mongoengine import NotUniqueError, ValidationError
from datetime import datetime

from submissions_api import app
from submissions_api.documents import Study, Submission


class SubmissionsTestCase(unittest.TestCase):

    def setUp(self):
        app.config['MONGODB_SETTINGS'] = {'DB': "testing"}
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True

        self.app = app.test_client()

        # Set the application context
        # (see http://kronosapiens.github.io/blog/2014/08/14
        # /understanding-contexts-in-flask.html)
        self.app_context = app.app_context()
        self.app_context.push()

        self.study = Study(
            name='Study 1', available_places=2, user='user_1').save()
        study = Study.objects.get(id=self.study.id)
        self.assertEqual(study.available_places, 2)
        self.assertEqual(study.user, 'user_1')

    def tearDown(self):
        self.app_context.pop()

        Study.drop_collection()
        Submission.drop_collection()

    def test_duplicate_study_name_errors(self):
        with self.assertRaises(NotUniqueError):
            Study(name='Study 1', available_places=2, user='user_1').save()

    def test_create_submission(self):
        field = Submission.created_at

        def mock_now():
            return datetime(2016, 1, 1)
        with patch.object(field, 'default', new=mock_now()):
            submission = Submission(study=self.study, user='user_2').save()

        submission = Submission.objects.get(id=submission.id)
        self.assertEqual(submission.study, self.study)
        self.assertEqual(submission.user, 'user_2')
        self.assertEqual(submission.created_at, datetime(2016, 1, 1))

    def test_no_duplicate_user_on_study(self):
        Submission(study=self.study, user='user_2').save()
        with self.assertRaises(NotUniqueError):
            Submission(study=self.study, user='user_2').save()

    def test_no_more_than_available_places_submissions(self):
        Submission(study=self.study, user='user_2').save()
        Submission(study=self.study, user='user_3').save()
        with self.assertRaises(ValidationError) as e:
            Submission(study=self.study, user='user_4').save()

        self.assertEqual(
            str(e.exception),
            "A maximum of 2 submissions allowed for the Study 1")


if __name__ == '__main__':
    unittest.main()
