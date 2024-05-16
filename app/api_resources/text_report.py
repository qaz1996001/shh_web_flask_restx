import re

import pandas as pd
from flask import jsonify, request
from flask_restx import Resource, Namespace
from sqlalchemy_filters import apply_filters
from ..schema import page_schema
from flask_marshmallow.fields import fields as mafields
from ..model import TextReportRawModel
from .. import db, ma

text_report_ns = Namespace('text_report', description='text report Resources')

########## for group_key ##############################
series_general_sort = {
    'patient_id': 100,
    'gender': 110,
    'age': 120,
    'study_date': 130,
    'study_time': 140,
    'study_description': 150,
    'accession_number': 160,
    'series_description': 170
}
series_general_pattern = re.compile(
    ('patient_id|gender|age|study_date|study_time|study_description|accession_number'))


def get_group_key_by_series(columns):
    return dict(
        general_keys=sorted(filter(lambda x: series_general_pattern.match(x) is not None, columns),
                            key=lambda x: series_general_sort.get(x, 999))
    )


########## for group_key ##############################

class PageSchema(ma.Schema):
    page = mafields.Integer(default=1)
    limit = mafields.Integer(default=20)
    sort = mafields.String(default='-uid')


class FilterSchema(ma.Schema):
    field = mafields.String()
    op = mafields.String()
    value = mafields.String()


page_schema = PageSchema()
filter_schema = FilterSchema()


########## query_filter( ##############################
def get_page_limit_sort(request, model, default=None):
    page_result = page_schema.dump(request.args, many=False)
    page = page_result['page']
    limit = page_result['limit']

    if request.args.get('sort'):
        sort = page_result['sort']
    else:
        sort = default
    order_by = sort[0]
    sort = sort[1:]
    sort_column = getattr(model, sort)
    if order_by == '+':
        sort_column = sort_column.asc()
    else:
        sort_column = sort_column.desc()
    return page, limit, sort_column


def get_query_filter(request):
    filter_dict = filter_schema.dump(request.args)
    if filter_dict:
        return [filter_dict]
    else:
        return None


filter_op_list = [  #'is_null',
    'is_not_null',
    '==', '!=',
    '>', '<',
    '>=', '<=',
    'like',
    #'ilike', 'not_ilike',
    'in',  #'not_in',
    #'any', 'not_any'
]


