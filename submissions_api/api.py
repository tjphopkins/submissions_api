from flask import request
import json
from mongoengine import NotUniqueError, ValidationError
from functools import wraps

from submissions_api import app
from submissions_api.documents import Study, Submission


@app.route('/')
def index():
    return "This is the index. Nothing to see here."


def jsonify_response(fn):
    """To be used as a decorator for converting endpoint response to json."""
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
    """Retrieves parameter from POST request and validates that it is a non-empty
    string.

    :arg param_name - str
    :return tuple containing:
        * valid - bool, indicating whether or not validaiton was successful
        * param_val - unicode, value retrieved from GET request
        * param_name - str, function argument
    """
    param_val = request.form.get(param_name)
    valid = isinstance(param_val, unicode) and param_val
    return valid, param_val, param_name


def _validate_post_params_or_error(param_names):
    """Given a list of paramaters, retrieves their values from POST request,
    validates them and returns a dict mapping params to values.

    :arg param_names - list(str)
    :return param_map - dict, maps params to values
    """
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
    """Handles studies POST request.

    POST params:
    * name - required, name of study to create
    * user - required, id of user creating the study
    * available_places - required, number of submissions allowed for this study

    :return dict containing success information and the created study if
    was successful.
    """
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
            name=param_map['name'],
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
    """
    Studies endpoint. Handles:
        * GET request to retrieve studies with optional user filter
            :return - dict containing success information and list of
                      studies if successful
        * POST request to create new study - see _studies_post method
    """
    if request.method == 'POST':
        return _studies_post()

    user = request.args.get('user')
    studies = _get_studies(user=user)

    return {
        'success': True,
        'studies': studies
    }


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
    """Handles submissions POST request.

    POST params:
    * study_id - required
    * user - required

    :return dict containing success information and the created submission if
    was successful.
    """
    params_to_validate = ['study_id', 'user']
    try:
        param_map = _validate_post_params_or_error(params_to_validate)
    except InvalidParam as e:
        return {
            'success': False,
            'message': str(e)
        }

    # Param validation successful
    try:
        submission = Submission.create_new(
            param_map['study_id'], param_map['user'])
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
    """
    Submissions endpoint. Handles:
        * GET request to retrieve submissions with optional user filter:
            :return - dict containing success information and list of
                      submissions if successful
        * POST request to create new submission (see _submissions_post method)
    """
    if request.method == 'POST':
        _submissions_post()

    user = request.args.get('user')
    if not user:
        return {
            'success': False,
            'message': "Must supply valid user_id"
        }
    submissions = _get_submissions_by_user(user)

    return {
        'success': True,
        'submissions': submissions
    }
