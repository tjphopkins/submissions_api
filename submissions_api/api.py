def study_conversion_to_dict(study):
    return {
        'id': str(study.id),
        'name': study.name,
        'available_places': study.available_places,
        'user': study.user
    }


def get_all_studies():
    from submissions_api.documents import Study # avoid circular import
    studies = Study.objects.all()
    return [study_conversion_to_dict(study) for study in studies]


def submission_conversion_to_dict(submission):
    return {
        'id': str(submission.id),
        'study_name': submission.study.name,
        'study_id': str(submission.study.id),
        'user': submission.user
    }
