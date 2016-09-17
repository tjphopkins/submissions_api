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


class InvalidParam(Exception):
    def __init__(self, param_name, param_val):
        self.param_name = param_name
        self.param_val = param_val

    def __str__(self):
        return "{value} is an invalid value for the parameter {param}".format(
            value=self.param_val, param=self.param_name)


def _get_and_validate_unicode_post_param(param_name):
    param_val = request.form.get(param_name)
    valid = param_val and isinstance(param_val, unicode)
    return valid, param_val, param_name


def _validate_post_params_or_error(param_names):
    validation_results = [_get_and_validate_unicode_post_param(param) for param
                          in param_names]
    param_map = {}
    for result in validation_results:
        valid, param_val, param_name = result
        if not valid:
            raise InvalidParam(param_name, param_val)
        param_map[param_name] = param_val
    return param_map


def _studies_post():
    params_to_validate = ['name', 'available_places', 'user']
    try:
        param_map = _validate_post_params_or_error(params_to_validate)
    except InvalidParam as e:
        return {
            'success': False,
            'message': str(e)
        }

    # Param validaiton successful
    try:
        study = Study(
            name=param_map['study_name'],
            available_places=int(param_map['available_places']),
            user=param_map['user']).\
            save()
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

    return studies


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


def _submissions_post():
    params_to_validate = ['study_id', 'user']
    try:
        param_map = _validate_post_params_or_error(params_to_validate)
    except InvalidParam as e:
        return {
            'success': False,
            'message': str(e)
        }

    # Param validaiton successful
    try:
        study = Study.objects.get(id=ObjectId(param_map['study_id']))
        submission = Submission(study=study, user=param_map['user']).save()
    except (NotUniqueError, ValidationError) as e:
        return {
            'success': False,
            'message': str(e)
        }
    else:
        return {
            'success': True,
            'submission': _submission_conversion_to_dict(submission)
        }


@app.route('/submissions', methods=['GET', 'POST'])
@jsonify_response
def submissions():
    if request.method == 'POST':
        _submissions_post()

    user = request.args.get('user')
    if not user:
        return{
            'success': False,
            'message': "Must supply value user_id"
        }
    studies = _get_submissions_by_user(user)

    return studies
