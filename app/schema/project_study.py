from flask_marshmallow.fields import fields as mafields
from flask_restx import Resource, fields, Namespace
from .base import UidFields
from .. import ma


class ProjectStudyAddStudySchema(ma.Schema):
    project_uid    = mafields.String(required=True)
    study_uid_list = mafields.List(mafields.String(required=True),required=True)


project_study_add_study_schema = ProjectStudyAddStudySchema()



field_model = {
    "study_uid"         :'ProjectStudyModel',
    "project_uid"       :'ProjectStudyModel',
    "extra_data"        :'ProjectStudyModel',
    "patient_uid"       :'PatientModel',
    "study_date"        :'PatientModel',
    "study_time"        :'StudyModel',
    "study_description" :'StudyModel',
    "accession_number"  :'StudyModel',
}

