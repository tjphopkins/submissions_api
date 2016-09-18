"""Test cases for Studies and Submissions application"""

import unittest
from mock import patch
from mongoengine import NotUniqueError, ValidationError
from datetime import datetime

from submissions_api import app
from submissions_api.documents import Study, Submission


class SubmissionsTestCase(unittest.TestCase):

    def setUp(self):
        # Set up testing DB
        app.config['MONGODB_SETTINGS'] = {'DB': "testing"}
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True

        self.app = app.test_client()

        # Set the application context
        # (see http://kronosapiens.github.io/blog/2014/08/14
        # /understanding-contexts-in-flask.html)
        self.app_context = app.app_context()
        self.app_context.push()

        # Clear out collections in the testing DB
        Study.drop_collection()
        Submission.drop_collection()

        self.study = Study(
            name='Study 1', available_places=2, user='user_1').save()
        study = Study.objects.get(id=self.study.id)
        self.assertEqual(study.available_places, 2)
        self.assertEqual(study.user, 'user_1')

    def tearDown(self):
        self.app_context.pop()

    def test_duplicate_study_name_errors(self):
        with self.assertRaises(NotUniqueError):
            Study(name='Study 1', available_places=2, user='user_1').save()

    def test_create_submission(self):
        field = Submission.created_at

        def mock_now():
            return datetime(2016, 1, 1)
        with patch.object(field, 'default', new=mock_now()):
            submission = Submission.create_new(self.study.id, 'user_2')

        submission = Submission.objects.get(id=submission.id)
        self.assertEqual(submission.study, self.study)
        self.assertEqual(submission.user, 'user_2')
        self.assertEqual(submission.created_at, datetime(2016, 1, 1))
        self.assertEqual(submission.study_submission_number, 0)

    def test_no_duplicate_user_on_study(self):
        Submission.create_new(self.study.id, 'user_2')
        with self.assertRaises(NotUniqueError):
            Submission.create_new(self.study.id, 'user_2').save()

    def test_no_more_than_available_places_submissions(self):
        Submission.create_new(self.study.id, 'user_2')
        Submission.create_new(self.study.id, 'user_3')
        with self.assertRaises(ValidationError) as e:
            Submission.create_new(self.study.id, 'user_4')

        self.assertEqual(
            str(e.exception),
            "A maximum of 2 submissions allowed for the Study 1")

    def test_concurrent_new_study_submission(self):
        submission_0 = Submission.create_new(self.study.id, 'user_1')
        self.assertEqual(submission_0.study_submission_number, 0)

        # Trick into thinking there are no submissions for this study
        # first time around, and then let it proceed as normal on the retry
        count_patcher = patch(
            'submissions_api.documents._get_study_submissions_count')
        mock_count = count_patcher.start()

        def return_0(*a, **k):
            count_patcher.stop()
            return 0

        mock_count.side_effect = return_0

        submission = Submission.create_new(self.study.id, 'user_2')
        self.assertEqual(submission.study_submission_number, 1)


if __name__ == '__main__':
    unittest.main()
