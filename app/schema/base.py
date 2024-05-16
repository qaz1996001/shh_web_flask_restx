from flask_marshmallow.fields import fields as mafields
from .. import ma


class PageSchema(ma.Schema):
    page = mafields.Integer(default=1)
    limit = mafields.Integer(default=20)
    sort = mafields.String(default='-uid')


page_schema = PageSchema()
