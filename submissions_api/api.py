def _study_conversion_to_dict(study):
    return {
        'id': str(study.id),
        'name': study.name,
        'available_places': study.available_places
    }


def get_all_studies():
    from submissions_api.documents import Study # avoid circular import
    studies = Study.objects.all()
    return [_study_conversion_to_dict(study) for study in studies]
