from flask import request
import json
from bson import ObjectId
from mongoengine import NotUniqueError, ValidationError

from submissions_api import app, api
from submissions_api.documents import Study, Submission


@app.route('/')
def index():
    return "This is the index. Nothing to see here."


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
                'study': api.study_conversion_to_dict(study)
            })

    studies = api.get_all_studies()
    return json.dumps(studies)


@app.route('/submissions', methods=['POST'])
def submissions():
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
            'submission': api.submission_conversion_to_dict(submission)
        })

    return
