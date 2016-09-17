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


def _get_and_validate_unicode_param(param_name):
    param_val = request.form.get(param_name)
    valid = param_val and isinstance(param_val, unicode)
    return valid, param_val, param_name


def _studies_post():
    params_to_validate = ['name', 'available_places', 'user']
    validation_results = [
        _get_and_validate_unicode_param(param) for param in params_to_validate]
    param_map = {}
    for result in validation_results:
        valid, param_val, param_name = result
        if not valid:
            return {
                'success': False,
                'message':
                "{value} is an invalid value for the parameter {param}".format(
                    value=param_val, param=param_name)
            }
        param_map[param_name] = param_val

    # Param validaiton successful
    try:
        study = Study(
            name=param_map['study_name'],
            available_places=int(param_map['available_places']),
            user=param_map['user']).\
            save()
    except (NotUniqueError, ValidationError) as e:
        return {
            'success': 'False',
            'message': str(e)
        }
    else:
        return {
            'success': 'True',
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
        return {
            'success': False,
            'message':
            "{value} is an invalid value for the parameter {param}".format(
                value=invalid_value, param=invalid_param)
        }

    try:
        study = Study.objects.get(id=ObjectId(study_id))
        submission = Submission(study=study, user=user).save()
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
