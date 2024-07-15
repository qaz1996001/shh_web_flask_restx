from flask_marshmallow.fields import fields as mafields
from flask_restx import fields
from .base import UidFields
from .. import ma

project_get = dict(project_uid=UidFields(attribute='uid'),
                   project_name=fields.String(attribute='name'),)

project_items_1 = {'project_uid': UidFields(attribute='uid'),
                   'project_name': fields.String(attribute='name')}