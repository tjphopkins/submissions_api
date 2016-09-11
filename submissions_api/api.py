from flask import request
import json
from bson import ObjectId
from mongoengine import NotUniqueError, ValidationError

from submissions_api import app
from submissions_api.documents import Study, Submission


@app.route('/')
def index():
    return "This is the index. Nothing to see here."


def _study_conversion_to_dict(study):
    return {
        'id': str(study.id),
        'name': study.name,
        'available_places': study.available_places,
        'user': study.user
    }


def _get_studies(user=None):
    if user:
        studies = Study.objects.filter(user=user)
    else:
        studies = Study.objects.all()
    return [_study_conversion_to_dict(study) for study in studies]


@app.route('/studies', methods=['GET', 'POST'])
def studies():
    if request.method == 'POST':
        name = request.form.get('name')
        available_places = request.form.get('available_places')
        user = request.form.get('user')

        success = True
        if not name or not isinstance(name, unicode):
            success = False
            invalid_param = "name"
            invalid_value = name
        elif not available_places or not isinstance(available_places, unicode):
            success = False
            invalid_param = "available_places"
            invalid_value = available_places
        elif not user or not isinstance(user, unicode):
            success = False
            invalid_param = "user"
            invalid_value = user

        if not success:
            return json.dumps({
                'success': False,
                'message':
                "{value} is an invalid value for the parameter {param}".format(
                    value=invalid_value, param=invalid_param)
            })

        try:
            study = Study(
                name=name, available_places=int(available_places),
                user=user).save()
        except (NotUniqueError, ValidationError) as e:
            return json.dumps({
                'success': False,
                'message': str(e)
            })
        else:
            return json.dumps({
                'success': True,
                'study': _study_conversion_to_dict(study)
            })

    user = request.args.get('user')
    # TODO: Some validation around user_id
    studies = _get_studies(user=user)

    return json.dumps(studies)


def _submission_conversion_to_dict(submission):
    return {
        'id': str(submission.id),
        'study_name': submission.study.name,
        'study_id': str(submission.study.id),
        'user': submission.user
    }


def _get_submissions_by_user(user):
    submissions = Submission.objects.filter(user=user)
    return [_submission_conversion_to_dict(submission) for
            submission in submissions]


@app.route('/submissions', methods=['GET', 'POST'])
def submissions():
    if request.method == 'POST':
        study_id = request.form.get('study')
        user = request.form.get('user')

        success = True
        if not study_id or not isinstance(study_id, unicode):
            success = False
            invalid_param = "study_id"
            invalid_value = study_id
        elif not user or not isinstance(user, unicode):
            success = False
            invalid_param = "user"
            invalid_value = user

        if not success:
            return json.dumps({
                'success': False,
                'message':
                "{value} is an invalid value for the parameter {param}".format(
                    value=invalid_value, param=invalid_param)
            })

        try:
            study = Study.objects.get(id=ObjectId(study_id))
            submission = Submission(study=study, user=user).save()
        except (NotUniqueError, ValidationError) as e:
            return json.dumps({
                'success': False,
                'message': str(e)
            })
        else:
            return json.dumps({
                'success': True,
                'submission': _submission_conversion_to_dict(submission)
            })

    user = request.args.get('user')
    if not user:
        return json.dumps({
            'success': False,
            'message': "Must supply value user_id"
        })
    studies = _get_submissions_by_user(user)

    return json.dumps(studies)
