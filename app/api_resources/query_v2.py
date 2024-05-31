import calendar
import datetime
import re
from typing import List

import flask_sqlalchemy.query
import orjson
from flask_restx import Resource, fields, Namespace
import uuid
import pandas as pd
from sqlalchemy import and_
from sqlalchemy.sql.expression import func
from sqlalchemy_filters import apply_filters
from flask import jsonify, request
from .base import UidFields
from ..model import ListStudyTextReportModel, ListStudyModel, ListPatientModel, ListProjectStudyModel, ProjectModel, \
    TextReportModel, SeriesModel, PatientModel, StudyModel, TextReportRawModel
from flask_marshmallow.fields import fields as mafields
from .. import db, ma

query_ns = Namespace('query_v2', description='query V2 Resources')

responses_data_model = query_ns.model('responses_data_model', {'total': fields.Integer,
                                                               'items': fields.List(
                                                                   fields.Raw),
                                                               })
responses_format_model = query_ns.model('responses_format_model',
                                        {'code': fields.Integer,
                                         'key': fields.List(fields.String),
                                         'data': fields.Nested(responses_data_model)}
                                        )
########## list_patient ###############################
query_list_patient_items = query_ns.model('query_list_patient_items',
                                          {'patient_uid': UidFields(),
                                           'patient_id': fields.String,
                                           'gender': fields.String,
                                           'age': fields.String,
                                           })
query_list_patient_data = query_ns.clone('query_list_patient_data',
                                         responses_data_model,
                                         {'items': fields.List(
                                             fields.Nested(query_list_patient_items))})

query_list_patient = query_ns.clone('query_list_patient',
                                    responses_format_model,
                                    {'data': fields.Nested(query_list_patient_data)})
########## list_patient ###############################

########## list_project ###############################
query_list_project_items_1 = query_ns.model('query_list_project_items_1',
                                            {'project_uid': UidFields(attribute='uid'),
                                             'project_name': fields.String(attribute='name'), })
query_list_project_items = query_ns.model('query_list_project_items',
                                          {'project_uid': UidFields(), 'project_name': fields.String, })
query_list_project_data = query_ns.clone('query_list_project_data',
                                         responses_data_model,
                                         {'items': fields.List(
                                             fields.Nested(query_list_project_items))})

query_list_project = query_ns.clone('query_list_project',
                                    responses_format_model,
                                    {'data': fields.Nested(query_list_project_data)})

########## list_project ###############################


########## list_project_series ########################
query_list_project_series = query_ns.model('query_list_project_series_get',
                                           {'project_uid': UidFields(),
                                            'project_name': fields.String,
                                            'series_uid': UidFields(attribute='uid'),
                                            'patient_id': fields.String,
                                            'gender': fields.String,
                                            'age': fields.String,
                                            'study_description': fields.String,
                                            'study_date': fields.String,
                                            'accession_number': fields.String,
                                            'modality': fields.String,
                                            'series_description': fields.String,
                                            })
# filter_list_project_series.default = """
#   [{
#     "field":"age",
#     "op":"ge",
#     "value":"0"},
#     {
#     "field":"series_description",
#     "op":"like",
#     "value":"%ADC%"}
#   ]
# """

########## list_project_series ########################

########## list_series ################################
query_list_series_items = query_ns.model('query_list_series_items', {'patient_id': fields.String,
                                                                     'gender': fields.String,
                                                                     'age': fields.String,
                                                                     'study_uid': UidFields(attribute='study_uid'),
                                                                     'study_date': fields.String,
                                                                     'study_description': fields.String,
                                                                     'accession_number': fields.String,
                                                                     'series_uid': UidFields(attribute='uid'),
                                                                     'series_description': fields.String,
                                                                     'modality': fields.String, })

query_list_series_data = query_ns.clone('query_list_series_data',
                                        responses_data_model,
                                        {'items': fields.List(
                                            fields.Nested(query_list_series_items))})

query_list_series = query_ns.clone('query_list_series',
                                   responses_format_model,
                                   {'data': fields.Nested(query_list_series_data)})
########## list_series ################################

########## list_study_text_report #####################
query_list_study_text_report_items_1 = query_ns.model('query_list_study_text_report_items_1',
                                                      {
                                                          'study_uid': UidFields(attribute='uid'),
                                                          'accession_number': fields.String,
                                                          'patient_id': fields.String,
                                                          'gender': fields.String,
                                                          'age': fields.String,
                                                          'study_date': fields.String,
                                                          'study_description': fields.String,
                                                          'text': fields.String,
                                                      })
query_list_study_text_report_items = query_ns.model('query_list_study_text_report_items',
                                                    {
                                                        'study_uid': UidFields(),
                                                        'accession_number': fields.String,
                                                        'patient_id': fields.String,
                                                        'gender': fields.String,
                                                        'age': fields.String,
                                                        'study_date': fields.String,
                                                        'study_description': fields.String,
                                                        'text': fields.String,
                                                    })

query_list_study_text_report_data = query_ns.clone('query_list_study_text_report_data',
                                                   responses_data_model,
                                                   {'items': fields.List(
                                                       fields.Nested(query_list_study_text_report_items))})

query_list_study_text_report = query_ns.clone('query_list_study_text_report',
                                              responses_format_model,
                                              {'data': fields.Nested(query_list_study_text_report_data)})
########## list_study_text_report #####################


########## for group_key ##############################
series_structure_sort = {
    "ADC": 100,
    "DWI0": 110,
    "DWI1000": 120,
    'T1_AXI': 300,
    'T1_COR': 311,
    'T1_SAG': 312,
    'T1CE_AXI': 320,
    'T1CE_COR': 321,
    'T1CE_SAG': 323,
    'T1FLAIR_AXI': 331,
    'T1FLAIR_COR': 332,
    'T1FLAIR_SAG': 333,
    'T1FLAIRCE_AXI': 341,
    'T1FLAIRCE_COR': 342,
    'T1FLAIRCE_SAG': 343,
    'T1CUBE_AXI': 350,
    'T1CUBE_COR': 351,
    'T1CUBE_SAG': 352,
    'T1CUBE_AXIr': 355,
    'T1CUBE_CORr': 356,
    'T1CUBE_SAGr': 357,
    'T1CUBECE_AXI': 361,
    'T1CUBECE_COR': 362,
    'T1CUBECE_SAG': 363,
    'T1CUBECE_AXIr': 365,
    'T1CUBECE_CORr': 366,
    'T1CUBECE_SAGr': 367,
    'T1FLAIRCUBE_AXI': 370,
    'T1FLAIRCUBE_COR': 371,
    'T1FLAIRCUBE_SAG': 372,
    'T1FLAIRCUBE_AXIr': 375,
    'T1FLAIRCUBE_CORr': 376,
    'T1FLAIRCUBE_SAGr': 377,
    'T1FLAIRCUBECE_AXI': 380,
    'T1FLAIRCUBECE_COR': 381,
    'T1FLAIRCUBECE_SAG': 382,
    'T1FLAIRCUBECE_AXIr': 385,
    'T1FLAIRCUBECE_CORr': 386,
    'T1FLAIRCUBECE_SAGr': 387,
    'T1BRAVO_AXI': 390,
    'T1BRAVO_COR': 391,
    'T1BRAVO_SAG': 392,
    'T1BRAVO_AXIr': 395,
    'T1BRAVO_CORr': 396,
    'T1BRAVO_SAGr': 397,
    'T1BRAVOCE_AXI': 400,
    'T1BRAVOCE_COR': 401,
    'T1BRAVOCE_SAG': 402,
    'T1BRAVOCE_AXIr': 405,
    'T1BRAVOCE_CORr': 406,
    'T1BRAVOCE_SAGr': 407,
    'T2_AXI': 410,
    'T2_COR': 411,
    'T2_SAG': 412,
    'T2CE_AXI': 420,
    'T2CE_COR': 421,
    'T2CE_SAG': 423,
    'T2FLAIR_AXI': 431,
    'T2FLAIR_COR': 432,
    'T2FLAIR_SAG': 433,
    'T2FLAIRCE_AXI': 441,
    'T2FLAIRCE_COR': 442,
    'T2FLAIRCE_SAG': 443,
    'T2CUBE_AXI': 450,
    'T2CUBE_COR': 451,
    'T2CUBE_SAG': 452,
    'T2CUBE_AXIr': 455,
    'T2CUBE_CORr': 456,
    'T2CUBE_SAGr': 457,
    'T2CUBECE_AXI': 461,
    'T2CUBECE_COR': 462,
    'T2CUBECE_SAG': 463,
    'T2CUBECE_AXIr': 465,
    'T2CUBECE_CORr': 466,
    'T2CUBECE_SAGr': 467,
    'T2FLAIRCUBE_AXI': 470,
    'T2FLAIRCUBE_COR': 471,
    'T2FLAIRCUBE_SAG': 472,
    'T2FLAIRCUBE_AXIr': 475,
    'T2FLAIRCUBE_CORr': 476,
    'T2FLAIRCUBE_SAGr': 477,
    'T2FLAIRCUBECE_AXI': 480,
    'T2FLAIRCUBECE_COR': 481,
    'T2FLAIRCUBECE_SAG': 482,
    'T2FLAIRCUBECE_AXIr': 485,
    'T2FLAIRCUBECE_CORr': 486,
    'T2FLAIRCUBECE_SAGr': 487,
    'T2BRAVO_AXI': 490,
    'T2BRAVO_COR': 491,
    'T2BRAVO_SAG': 492,
    'T2BRAVO_AXIr': 495,
    'T2BRAVO_CORr': 496,
    'T2BRAVO_SAGr': 497,
    'T2BRAVOCE_AXI': 500,
    'T2BRAVOCE_COR': 501,
    'T2BRAVOCE_SAG': 502,
    'T2BRAVOCE_AXIr': 505,
    'T2BRAVOCE_CORr': 506,
    'T2BRAVOCE_SAGr': 507,
}

series_general_pattern = re.compile(
    ('patient_id|gender|age|study_date|study_time|study_description|accession_number'))
series_structure_pattern = re.compile(('T1|T2|DWI|ADC'))
series_special_pattern = re.compile(('MRA|SWAN|eSWAN'))
series_perfusion_pattern = re.compile(('DSC|ASL'))
series_functional_pattern = re.compile(('RESTING|CVR|DTI'))
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
series_special_sort = {
    'MRA_BRAIN': 100,
    'MRA_NECK': 110,
    'MRAVR_BRAIN': 120,
    'MRAVR_NECK': 130,
    'SWAN': 200,
    'SWANmIP': 210,
    'SWANPHASE': 210,
    'eSWAN': 300,
    'eSWANmIP': 310,
    'eSWANPHASE': 330,
}
series_perfusion_sort = {
    'ASLSEQ': 100,
    'ASLSEQATT': 110,
    'ASLSEQATT_COLOR': 111,
    'ASLSEQCBF': 120,
    'ASLSEQCBF_COLOR': 121,
    'ASLPROD': 130,
    'ASLPRODCBF': 140,
    'ASLPRODCBF_COLOR': 141,
    'ASLSEQPW': 150,
    'DSC': 200,
    'DSCCBF_COLOR': 210,
    'DSCCBV_COLOR': 220,
    'DSCMTT_COLOR': 230,

}
series_functional_sort = {
    'RESTING': 100,
    'RESTING2000': 101,
    'CVR': 200,
    'CVR1000': 201,
    'CVR2000': 202,
    'CVR2000_EAR': 203,
    'CVR2000_EYE': 204,
    'DTI32D': 300,
    'DTI64D': 330
}


def get_group_key_by_series(columns):
    return dict(
        general_keys=sorted(filter(lambda x: series_general_pattern.match(x) is not None, columns),
                            key=lambda x: series_general_sort.get(x, 999)),
        structure_keys=sorted(filter(lambda x: series_structure_pattern.match(x) is not None, columns),
                              key=lambda x: series_structure_sort.get(x, 999)),
        special_keys=sorted(filter(lambda x: series_special_pattern.match(x) is not None, columns),
                            key=lambda x: series_special_sort.get(x, 999)),
        perfusion_keys=sorted(filter(lambda x: series_perfusion_pattern.match(x) is not None, columns),
                              key=lambda x: series_perfusion_sort.get(x, 999)),
        functional_keys=sorted(filter(lambda x: series_functional_pattern.match(x) is not None, columns),
                               key=lambda x: series_functional_sort.get(x, 999))
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


#
query_filter_items = query_ns.model('query_filter_items',
                                    {"field": fields.String(),
                                     "op": fields.String(),
                                     "value": fields.String(), })

filter_list_project_series = fields.List(fields.Nested(query_filter_items))

filter_list_project_series.default = """
  [{
    "field":"age",
    "op":"ge",
    "value":"0"},
    {
    "field":"series_description",
    "op":"like",
    "value":"%ADC%"}
  ]
"""
query_filter_list_project_series = query_ns.model('query_filter_list_project_series',
                                                  {"filter_": filter_list_project_series, })

filter_list_study_text_report = fields.List(fields.Nested(query_filter_items))
filter_list_study_text_report.default = """
  [{
    "field":"is_success",
    "op":"eq",
    "value":"1"},
    {
    "field":"text",
    "op":"like",
    "value":"%Stroke (-C +C)%"}
  ]
"""
query_filter_list_study_text_report = query_ns.model('query_filter_list_study_text_report',
                                                     {"filter_": filter_list_study_text_report, })

filter_op_list = [  #'is_null',
    'like',
    '==',
    '>', '<',
    '>=', '<=', '!=',
    'regexp',
    'is_not_null', 'in',  #'not_in',
    #'ilike', 'not_ilike',

    #'any', 'not_any'
]


# use map
def op_like_add_percent(x):
    if x['op'] == 'like':
        if x['value'].startswith('%') or x['value'].endswith('%'):
            pass
        else:
            x['value'] = rf"%{x['value']}%"
    return x


# use filter
def get_orther_filter(x):
    if (x['field'] != 'impression_str') and (x['op'] != 'regexp'):
        return True
    elif x['op'] == 'regexp':
        return False
    elif x['field'] == 'impression_str':
        return False
    return True


# use filter
# def get_impression_str_filter(x):
#     return []

def get_regexp_filter(x):
    if x['op'] == 'regexp':
        return True
    return False


def get_regexp(regexp_filter_list, model):
    regexp_list = []
    for i in regexp_filter_list:
        column = getattr(model, i['field'])
        regexp_list.append(column.regexp_match(i['value'], flags='i'))
    return regexp_list


########## query_filter( ##############################

@query_ns.route('/')
@query_ns.route('/upload')
class QueryResources(Resource):
    def get(self, ):
        route_str = request.url.split('/')[-1]
        if route_str == 'upload':
            print(route_str)
            self.upload_list_patient_table()
            self.upload_list_study_table()

        # reslut = query.filter(TextReportModel.text.regexp_match('Stroke')).all()
        # print(reslut)
        # print(db.select(ListStudyTextReportModel).where(ListStudyTextReportModel.text.regexp_match('.*Stroke.*')))
        paginate = db.paginate(
            db.select(ListStudyTextReportModel).where(ListStudyTextReportModel.text.regexp_match('\dmm')),
            page=1,
            per_page=100
        )
        patient_model_list = paginate.items
        print('patient_model_list')
        print(len(patient_model_list))
        total = paginate.total
        result = query_ns.marshal(patient_model_list, query_list_study_text_report_items)
        group_key = get_group_key_by_series(query_list_patient_items.keys())
        jsonify_result = {'code': 2000,
                          'key': list(query_list_study_text_report_items.keys()),
                          'data': {"total": total,
                                   "items": result},
                          'group_key': group_key
                          }
        return jsonify(jsonify_result)
        # return 'QueryResources V2'

    def post(self, ):
        series_model: SeriesModel = db.session.execute(
            db.select(SeriesModel).where(SeriesModel.uid == 'eb6509c7-9074-4e1e-971a-f9b3e81040de')
        ).scalar()
        print(series_model.project[0].name)
        print(series_model.project[1].name)
        return 'QueryResources'

    def list_patient_table(self):
        pass

    def upload_list_patient_table(self):

        db_df = pd.read_sql('select * from patient where deleted_at is null', con=db.engine)
        db_df['birth_date'] = pd.to_datetime(db_df['birth_date'])
        db_df['age'] = db_df['birth_date'].map(self.get_age_by_patient)
        db_df = db_df[['uid', 'patient_id', 'gender', 'age']]
        db_df.columns = ['patient_uid', 'patient_id', 'gender', 'age']
        count = db_df.to_sql(name='list_patient', con=db.engine, if_exists='append', index=False)
        return count

    def upload_list_study_table(self):
        db_df = pd.read_sql('select * from study join patient on study.patient_uid = patient.uid', con=db.engine)
        db_df['birth_date'] = pd.to_datetime(db_df['birth_date'])
        db_df['study_date'] = pd.to_datetime(db_df['study_date'])
        db_df.columns = ['study_uid', 'patient_uid', 'study_date', 'study_time', 'study_description',
                         'accession_number', 'orthanc_study_ID', 'created_at', 'updated_at',
                         'deleted_at', 'uid', 'patient_id', 'gender', 'birth_date',
                         'orthanc_patient_ID', 'created_at', 'updated_at', 'deleted_at']

        db_df['age'] = db_df[['birth_date', 'study_date']].apply(self.get_age_by_study_date, axis=1)
        db_df = db_df[['study_uid', 'patient_id', 'gender',
                       'age', 'study_date', 'study_time', 'study_description', 'accession_number']]

        db_df.columns = ['study_uid', 'patient_id', 'gender',
                         'age', 'study_date', 'study_time', 'study_description', 'accession_number']
        self.db_series_df = pd.read_sql('select * from series where deleted_at is null', con=db.engine)
        db_df = db_df.apply(self.get_series_description_json, axis=1)
        db_df[['study_date', 'study_time']] = db_df[['study_date', 'study_time']].astype(str)

        db_df['study_time'] = db_df['study_time'].map(lambda x: x.split('.')[0])
        session = db.session()
        error_case_list = []
        for index, row in db_df.iterrows():
            try:
                list_study_model = ListStudyModel()
                if isinstance(row['study_uid'], str):
                    list_study_model.study_uid = uuid.UUID(row['study_uid'])
                else:
                    list_study_model.study_uid = row['study_uid']
                list_study_model.patient_id = row['patient_id']
                list_study_model.gender = row['gender']
                list_study_model.age = row['age']
                list_study_model.study_date = datetime.datetime.strptime(row['study_date'], '%Y-%m-%d').date()
                list_study_model.study_time = datetime.datetime.strptime(row['study_time'], '%H:%M:%S').time()
                list_study_model.study_description = row['study_description']
                list_study_model.accession_number = row['accession_number']
                list_study_model.series_description = row['series_description']
                session.add(list_study_model)
            except:
                error_case_list.append(row['study_uid'])
        session.commit()

    def upload_list_study_text_report_table(self):
        pass

    @staticmethod
    def get_age_by_patient(birth_date):
        birth_date = birth_date
        datetime_now = datetime.datetime.now()
        year = datetime_now.year - birth_date.year
        month = datetime_now.month - birth_date.month
        if month < 0:
            year = year - 1
            month = 12 + month
        day_list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if calendar.isleap(datetime_now.year):  # 判斷如果是閏年
            day_list[1] = 29  # 就將二月份的天數改成 29 天
        day = datetime_now.day - birth_date.day
        if day < 0:
            month = month - 1
            if month < 0:
                year = year - 1
                month = 12 + month
            day = day_list[month] + day
        return year

    @staticmethod
    def get_age_by_study_date(row):
        birth_date = row['birth_date']
        study_date = row['study_date']
        year = study_date.year - birth_date.year
        month = study_date.month - birth_date.month
        if month < 0:
            year = year - 1
            month = 12 + month
        day_list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if calendar.isleap(study_date.year):  # 判斷如果是閏年
            day_list[1] = 29  # 就將二月份的天數改成 29 天
        day = study_date.day - birth_date.day
        if day < 0:
            month = month - 1
            if month < 0:
                year = year - 1
                month = 12 + month
            day = day_list[month] + day
        return year

    def get_series_description_json(self, row):
        db_series_df = self.db_series_df
        study_uid = row['study_uid']
        result = db_series_df[db_series_df['study_uid'] == study_uid]['series_description'].value_counts().to_dict()
        row['series_description'] = result
        return row


@query_ns.route('/list_patient')
@query_ns.param('page', type=int, default=1)
@query_ns.param('limit', type=int, default=20)
@query_ns.param('sort', type=str, default='+patient_id')
class QueryPatientResources(Resource):

    # @query_ns.marshal_with(query_list_patient)
    @query_ns.response(code=200,
                       description='Success',
                       model=query_list_patient)
    def get(self, ):
        page, limit, sort_column = get_page_limit_sort(request=request, model=ListPatientModel, default='+patient_id')
        print(page)
        print(limit)
        print(sort_column)
        paginate = db.paginate(
            db.select(ListPatientModel).order_by(sort_column),
            page=page,
            per_page=limit
        )
        patient_model_list = paginate.items
        total = paginate.total
        result = query_ns.marshal(patient_model_list, query_list_patient_items)
        group_key = get_group_key_by_series(query_list_patient_items.keys())
        jsonify_result = {'code': 2000,
                          'key': list(query_list_patient_items.keys()),
                          'data': {"total": total,
                                   "items": result},
                          'group_key': group_key
                          }
        return jsonify(jsonify_result)


@query_ns.route('/list_study')
@query_ns.param('page', type=int)
@query_ns.param('limit', type=int)
@query_ns.param('sort', type=str)
class QueryStudyResources(Resource):
    list_study_filter_op_list = filter_op_list

    def get(self, ):
        page, limit, sort_column = get_page_limit_sort(request=request, model=ListStudyModel, default='+study_uid')
        query = ListStudyModel.query
        filter_ = get_query_filter(request=request)
        if filter_:
            series_description_filter = list(filter(lambda x: x['field'] == 'series_description', filter_))
            orther_filter = list(filter(lambda x: x['field'] != 'series_description', filter_))
            filtered_query = apply_filters(query, orther_filter)
            paginate = (filtered_query.filter(ListStudyModel.
                                              series_description.op("->")(
                series_description_filter[0]['field']) is not None).
                        order_by(sort_column).paginate(page=page,
                                                       per_page=limit))
        else:
            paginate = query.order_by(sort_column).paginate(page=page,
                                                            per_page=limit)
        list_study_model_result = paginate.items
        total = paginate.total
        # response_list = list(map(lambda x: x.to_dict(), list_study_model_result))
        response_list = list(map(self.get_series_description_json, list_study_model_result))
        df = pd.json_normalize(response_list)
        columns = list(
            map(lambda x: x.replace('series_description.', '') if 'series_description.' in x else x, df.columns))
        df.columns = columns
        group_key = get_group_key_by_series(columns)
        df.fillna(0, inplace=True)
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': self.list_study_filter_op_list
                          }
        return jsonify(jsonify_result)

    def post(self, ):
        page, limit, sort_column = get_page_limit_sort(request=request, model=ListStudyModel, default='+study_uid')
        query = ListStudyModel.query
        filter_ = filter_schema.dump(request.json['filter_'], many=True)
        if filter_:
            series_description_filter = list(filter(lambda x: x['field'] == 'series_description', filter_))
            series_description_filter = list(
                map(lambda x: and_(ListStudyModel.series_description.op("->>")(x['value']).is_not(None)),
                    series_description_filter))
            orther_filter = list(filter(lambda x: x['field'] != 'series_description', filter_))
            filtered_query = apply_filters(query, orther_filter)
            paginate = (filtered_query.filter(*series_description_filter).order_by(sort_column).paginate(page=page,
                                                                                                         per_page=limit))
            print(filtered_query.filter(*series_description_filter).order_by(sort_column))
        else:
            paginate = query.order_by(sort_column).paginate(page=page,
                                                            per_page=limit)

        list_study_model_result = paginate.items
        total = paginate.total
        print(total)
        # response_list = list(map(lambda x: x.to_dict(), list_study_model_result))
        response_list = list(map(self.get_series_description_json, list_study_model_result))
        df = pd.json_normalize(response_list)
        columns = list(
            map(lambda x: x.replace('series_description.', '') if 'series_description.' in x else x, df.columns))
        df.columns = columns
        group_key = get_group_key_by_series(columns)
        df.fillna(0, inplace=True)
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': self.list_study_filter_op_list
                          }
        return jsonify(jsonify_result)

    def get_series_description_json(self, list_study_model: ListStudyModel):
        list_study_model_dict = list_study_model.to_dict()
        if isinstance(list_study_model.series_description, str):
            series_description = orjson.loads(list_study_model.series_description)
        else:
            series_description = list_study_model.series_description
        list_study_model_dict.update(series_description)
        list_study_model_dict.pop('series_description')
        return list_study_model_dict


@query_ns.route('/list_project')
@query_ns.param('page', type=int, default=1)
@query_ns.param('limit', type=int, default=20)
@query_ns.param('sort', type=str, default='+uid')
class QueryListProjectResources(Resource):
    @query_ns.response(code=200,
                       description='Success',
                       model=query_list_project)
    def get(self, ):
        page, limit, sort_column = get_page_limit_sort(request=request, model=ProjectModel, default='+uid')
        query = ProjectModel.query
        paginate = query.order_by(sort_column).paginate(page=page,
                                                        per_page=limit)
        list_project_result = paginate.items
        total = paginate.total

        response_list = list(map(lambda x: x.to_dict(), list_project_result))
        df: pd.DataFrame = pd.json_normalize(response_list)
        columns = list(query_list_project_items.keys())
        items = query_ns.marshal(df.to_dict(orient='records'),
                                 query_list_project_items_1)
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": items},
                          }
        return jsonify(jsonify_result)


@query_ns.route('/list_project_series')
class QueryListProjectSeriesResources(Resource):
    def get(self):
        page, limit, sort_column = get_page_limit_sort(request=request, model=ListProjectStudyModel, default='+uid')
        query = ListProjectStudyModel.query
        filter_ = get_query_filter(request=request)
        if filter_:
            filtered_query = apply_filters(query, filter_)
            paginate = filtered_query.order_by(sort_column).paginate(page=page,
                                                                     per_page=limit)
            print(filtered_query)
        else:
            paginate = query.order_by(sort_column).paginate(page=page,
                                                            per_page=limit)
        list_project_series_result = paginate.items
        total = paginate.total

        response_list = list(map(lambda x: x.to_dict(), list_project_series_result))
        df: pd.DataFrame = pd.json_normalize(response_list)
        columns = list(
            map(lambda x: x.replace('series_description.', '') if 'series_description.' in x else x, df.columns))
        df.columns = columns

        df.fillna(0, inplace=True)
        group_key = get_group_key_by_series(columns)
        group_key['general_keys'].insert(0, 'project_name')
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key
                          }
        return jsonify(jsonify_result)

    @query_ns.param('page', type=int, default=1)
    @query_ns.param('limit', type=int, default=20)
    @query_ns.param('sort', type=str, default='+project_name')
    @query_ns.expect(query_filter_list_project_series)
    def post(self):
        # print(request.args)
        # print(request.json)
        # print(filter_schema.dump(request.json['filter_'], many=True))
        page, limit, sort_column = get_page_limit_sort(request=request, model=ListProjectStudyModel)
        query = ListProjectStudyModel.query
        filter_ = filter_schema.dump(request.json['filter_'], many=True)
        print(filter_)
        if filter_:
            # filtered_query = apply_filters(query, filter_)
            # paginate = filtered_query.order_by(sort_column).paginate(page=page,
            #                                                          per_page=limit)
            series_description_filter = list(filter(lambda x: x['field'] == 'series_description', filter_))
            series_description_filter = list(
                map(lambda x: and_(ListProjectStudyModel.series_description.op("->>")(x['value']).is_not(None)),
                    series_description_filter))
            orther_filter = list(filter(lambda x: x['field'] != 'series_description', filter_))
            filtered_query = apply_filters(query, orther_filter).filter(*series_description_filter).order_by(sort_column)
            paginate = filtered_query.paginate(page=page,
                                               per_page=limit)
            print(filtered_query)
        else:
            paginate = query.order_by(sort_column).paginate(page=page,
                                                            per_page=limit)
        list_project_series_result = paginate.items
        total = paginate.total

        response_list = list(map(lambda x: x.to_dict(), list_project_series_result))
        df: pd.DataFrame = pd.json_normalize(response_list)
        columns = list(
            map(lambda x: x.replace('series_description.', '') if 'series_description.' in x else x, df.columns))
        df.columns = columns
        group_key = get_group_key_by_series(columns)
        group_key['general_keys'].insert(0, 'project_name')
        df.fillna(0, inplace=True)
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': filter_op_list}
        return jsonify(jsonify_result)


@query_ns.route('/list_study_text_report')
class QueryListStudyTextReportResources(Resource):
    pattern_impression_str = re.compile(r'(?i:impression\s?:?|imp:?|conclusions?:?)')
    pattern_depiction = re.compile(r'Summary :\n(.*)(\n.+)醫師', re.DOTALL)

    # @query_ns.marshal_with(query_list_study_text_report)
    @query_ns.param('page', type=int, default='1')
    @query_ns.param('limit', type=int, default='20')
    @query_ns.param('sort', type=str, default='+study_uid')
    def get(self):
        page, limit, sort_column = get_page_limit_sort(request=request, model=ListStudyTextReportModel,
                                                       default='+study_uid')
        query = ListStudyTextReportModel.query
        filter_ = get_query_filter(request=request)
        if filter_:
            impression_str_filter = list(filter(lambda x: x['field'] == 'impression_str', filter_))
            orther_filter = list(filter(lambda x: x['field'] != 'impression_str', filter_))
            orther_filter = list(map(op_like_add_percent, orther_filter))
            # filtered_query = apply_filters(query, filter_)
            filtered_query = apply_filters(query, orther_filter)
            paginate = filtered_query.order_by(sort_column).paginate(page=page,
                                                                     per_page=limit)
            print(filtered_query)
        else:
            paginate = (query.order_by(sort_column)
                        .filter(ListStudyTextReportModel.is_success == 1)
                        .paginate(page=page, per_page=limit))

        list_study_text_result = paginate.items
        total = paginate.total

        response_list = list(map(lambda x: x.to_dict(), list_study_text_result))
        df: pd.DataFrame = pd.json_normalize(response_list)
        df['impression_str'] = df['text'].map(self.get_impression_str)
        columns = df.columns.to_list()
        group_key = get_group_key_by_series(columns)
        group_key['general_keys'].append('text')
        group_key['general_keys'].append('impression_str')
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': filter_op_list}
        return jsonify(jsonify_result)

    # def gtemp(self):
    @query_ns.param('page', type=int, default='1')
    @query_ns.param('limit', type=int, default='20')
    @query_ns.param('sort', type=str, default='+study_uid')
    @query_ns.expect(query_filter_list_study_text_report)
    def post(self):
        print(request.args)
        print(request.json)
        # print(filter_schema.dump(request.json['filter_'], many=True))
        page, limit, sort_column = get_page_limit_sort(request=request, model=ListStudyTextReportModel)
        query = ListStudyTextReportModel.query
        filter_ = filter_schema.dump(request.json['filter_'], many=True)
        if filter_:
            impression_str_filter = list(filter(lambda x: x['field'] == 'impression_str', filter_))
            # orther_filter = list(filter(lambda x: x['field'] != 'impression_str', filter_))
            orther_filter = list(filter(get_orther_filter, filter_))
            orther_filter = list(map(op_like_add_percent, orther_filter))
            regexp_filter = list(filter(get_regexp_filter, filter_))
            regexp_list = get_regexp(regexp_filter, ListStudyTextReportModel)
            # regexp_filter = list(
            #     map(lambda x: and_(ListStudyTextReportModel..op("->>")(x['value']).is_not(None)),
            #         regexp_filter))
            print('orther_filter')
            print(orther_filter)
            print('regexp_filter')
            print(regexp_filter)
            print('regexp_list')
            print(regexp_list)
            filtered_query = apply_filters(query, orther_filter)
            temp_query = filtered_query \
                .filter(ListStudyTextReportModel.is_success == 1) \
                .filter(*regexp_list) \
                .order_by(sort_column)
            print('temp_query')
            print(temp_query)
            print(type(temp_query))
            paginate = temp_query.paginate(page=page, per_page=limit)
        else:
            paginate = query.order_by(sort_column).paginate(page=page,
                                                            per_page=limit)
        list_study_text_result = paginate.items
        total = paginate.total
        response_list = list(map(lambda x: x.to_dict(), list_study_text_result))
        df: pd.DataFrame = pd.json_normalize(response_list)
        df['impression_str'] = df['text'].map(self.get_impression_str)
        columns = df.columns.to_list()
        group_key = get_group_key_by_series(columns)
        group_key['general_keys'].append('text')
        group_key['general_keys'].append('impression_str')
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': filter_op_list}
        return jsonify(jsonify_result)

    def get_impression_str(self, x):
        # result_impression_str = pattern_impression_str.search(x)
        depiction_match = self.pattern_depiction.search(x)
        if depiction_match:
            depiction = depiction_match.group(1)
            result_impression_str = self.pattern_impression_str.split(depiction)
            if len(result_impression_str) > 0:
                return result_impression_str[-1]
            else:
                return ''
        return ''


@query_ns.route('/text_report')
class TextRepostStudyResources(Resource):
    pattern_impression_str = re.compile(r'(?i:impression\s?:?|imp:?|conclusions?:?)')
    pattern_depiction = re.compile(r'Summary :\n(.*)(\n.+)醫師', re.DOTALL)

    # @query_ns.marshal_with(query_list_study_text_report)
    @query_ns.param('page', type=int, default='1')
    @query_ns.param('limit', type=int, default='20')
    def get(self):
        page, limit, sort_column = get_page_limit_sort(request=request, model=TextReportRawModel,
                                                       default='+accession_number')
        query = TextReportRawModel.query
        filter_ = get_query_filter(request=request)
        if filter_:
            impression_str_filter = list(filter(lambda x: x['field'] == 'impression_str', filter_))
            orther_filter = list(filter(lambda x: x['field'] != 'impression_str', filter_))
            filtered_query = apply_filters(query, orther_filter)
            paginate = filtered_query.order_by(sort_column).paginate(page=page,
                                                                     per_page=limit)
            print(filtered_query)
        else:
            paginate = (query.order_by(sort_column)
                        .filter(func.char_length(TextReportRawModel.text) > 0)
                        .paginate(page=page, per_page=limit))
        text_report_result = paginate.items
        response_list = list(map(lambda x: x.to_dict(), text_report_result))
        total = paginate.total
        df: pd.DataFrame = pd.json_normalize(response_list)
        df['impression_str'] = df['text'].map(self.get_impression_str)
        columns = df.columns.to_list()
        group_key = get_group_key_by_series(columns)
        group_key['general_keys'].append('text')
        group_key['general_keys'].append('impression_str')
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': filter_op_list}
        return jsonify(jsonify_result)

    @query_ns.param('page', type=int, default='1')
    @query_ns.param('limit', type=int, default='20')
    def post(self):
        page, limit, sort_column = get_page_limit_sort(request=request, model=TextReportRawModel,
                                                       default='+accession_number')

        filter_ = filter_schema.dump(request.json['filter_'], many=True)
        if filter_:
            impression_str_filter = list(filter(lambda x: x['field'] == 'impression_str', filter_))
            # orther_filter = list(filter(lambda x: x['field'] != 'impression_str', filter_))
            orther_filter = list(filter(get_orther_filter, filter_))
            orther_filter = list(map(op_like_add_percent, orther_filter))
            regexp_filter = list(filter(get_regexp_filter, filter_))
            regexp_list = get_regexp(regexp_filter, TextReportRawModel)
            # print('orther_filter')
            # print(orther_filter)
            # print('regexp_filter')
            # print(regexp_filter)
            # print('regexp_list')
            # print(regexp_list)
            filtered_query = apply_filters(TextReportRawModel.query, orther_filter)
            query = filtered_query \
                .filter(*regexp_list)
            print('query')
            print(query)
        else:
            impression_str_filter = None
            query = TextReportRawModel.query
        paginate = (query.order_by(sort_column)
                    .filter(func.char_length(TextReportRawModel.text) > 0)
                    .paginate(page=page, per_page=limit))

        text_report_result = paginate.items
        response_list = list(map(lambda x: x.to_dict(), text_report_result))
        total = paginate.total
        df: pd.DataFrame = pd.json_normalize(response_list)

        df['impression_str'] = df['text'].map(self.get_impression_str)
        if impression_str_filter:
            temp_list = []
            for i in impression_str_filter:
                temp_list.append(df['impression_str'].str.contains(i['value']))
            temp_df = pd.DataFrame(temp_list).T
            df_filter = df[temp_df.all(axis=1)]
        else:
            df_filter = df
        columns = df_filter.columns.to_list()
        group_key = get_group_key_by_series(columns)
        group_key['general_keys'].append('text')
        group_key['general_keys'].append('impression_str')
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df_filter.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': filter_op_list}
        return jsonify(jsonify_result)

        # columns = df.columns.to_list()
        # group_key = get_group_key_by_series(columns)
        # group_key['general_keys'].append('text')
        # group_key['general_keys'].append('impression_str')
        # jsonify_result = {'code': 2000,
        #                   'key': columns,
        #                   'data': {"total": total,
        #                            "items": df.to_dict(orient='records')},
        #                   'group_key': group_key,
        #                   'op_list': filter_op_list}
        # return jsonify(jsonify_result)

    def delete(self):
        return 'TextRepostStudyResources'

    def get_impression_str(self, x):
        # result_impression_str = pattern_impression_str.search(x)
        depiction_match = self.pattern_depiction.search(x)
        if depiction_match:
            depiction = depiction_match.group(1)
            result_impression_str = self.pattern_impression_str.split(depiction)
            if len(result_impression_str) > 0:
                return result_impression_str[-1]
            else:
                return ''
        return ''


@query_ns.route('/list_study/download')
class QueryStudyDownloadResources(QueryStudyResources):
    def post(self):
        # req = request.json
        # print(req)
        # return 'QueryStudyDownloadResources'
        page, limit, sort_column = get_page_limit_sort(request=request, model=ListStudyModel, default='+study_uid')
        query = ListStudyModel.query
        filter_ = filter_schema.dump(request.json['filter_'], many=True)
        if filter_:
            series_description_filter = list(filter(lambda x: x['field'] == 'series_description', filter_))
            series_description_filter = list(
                map(lambda x: and_(ListStudyModel.series_description.op("->>")(x['value']).is_not(None)),
                    series_description_filter))
            orther_filter = list(filter(lambda x: x['field'] != 'series_description', filter_))
            filtered_query = apply_filters(query, orther_filter)
            paginate = (filtered_query.filter(*series_description_filter))
        else:
            paginate = query

        list_study_model_result = db.session.execute(paginate.order_by(sort_column)).all()
        list_study_model_result = list(map(lambda x: x[0], list_study_model_result))
        print(list_study_model_result)
        response_list = list(map(self.get_series_description_json, list_study_model_result))
        df = pd.json_normalize(response_list)
        columns = list(
            map(lambda x: x.replace('series_description.', '') if 'series_description.' in x else x, df.columns))
        df.columns = columns
        group_key = get_group_key_by_series(columns)
        df.fillna(0, inplace=True)
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": df.shape[0],
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': self.list_study_filter_op_list
                          }
        return jsonify(jsonify_result)
