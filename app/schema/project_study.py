from flask_marshmallow.fields import fields as mafields
from .. import ma


class ProjectStudyAddStudySchema(ma.Schema):
    project_uid    = mafields.String(required=True)
    study_uid_list = mafields.List(mafields.String(required=True),required=True)


project_study_add_study_schema = ProjectStudyAddStudySchema()