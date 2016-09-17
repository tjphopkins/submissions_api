from flask import request
import json
from bson import ObjectId
from mongoengine import NotUniqueError, ValidationError
from functools import wraps

from submissions_api import app
from submissions_api.documents import Study, Submission


@app.route('/')
def index():
    return "This is the index. Nothing to see here."


def jsonify_response(fn):
    @wraps(fn)
    def fn_wrapper(*args, **kwargs):
        return json.dumps(fn(*args, **kwargs))
    return fn_wrapper


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


def _unicode_param_validation(param_val):
    return not param_val or not isinstance(param_val, unicode)


def _studies_post():
    study_name = request.form.get('name')
    available_places = request.form.get('available_places')
    user = request.form.get('user')

    success = True
    if _unicode_param_validation(study_name):
        success = False
        invalid_param = "name"
        invalid_value = study_name
    elif _unicode_param_validation(available_places):
        success = False
        invalid_param = "available_places"
        invalid_value = available_places
    elif _unicode_param_validation(user):
        success = False
        invalid_param = "user"
        invalid_value = user

    if not success:
        return {
            'success': False,
            'message':
            "{value} is an invalid value for the parameter {param}".format(
                value=invalid_value, param=invalid_param)
        }

    try:
        study = Study(
            name=study_name, available_places=int(available_places),
            user=user).save()
    except (NotUniqueError, ValidationError) as e:
        return {
            'success': False,
            'message': str(e)
        }
    else:
        return {
            'success': True,
            'study': _study_conversion_to_dict(study)
        }


@app.route('/studies', methods=['GET', 'POST'])
@jsonify_response
def studies():
    if request.method == 'POST':
        return _studies_post()

    user = request.args.get('user')
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
@jsonify_response
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

    return studies
