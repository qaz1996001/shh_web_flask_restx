from copy import copy
import orjson
from flask_restx import Resource, fields, Namespace
import datetime
import pathlib
import time
import uuid
from typing import List
import pandas as pd
from sqlalchemy.sql.expression import func,distinct

from flask import jsonify, request
from .base import UidFields, CountFields
from ..model import PatientModel, StudyModel, ProjectModel, ProjectSeriesModel, TextReportModel, \
    SeriesModel
from .series import SeriesResources
from .study import StudyResources
from .patient import PatientResources

from flask_marshmallow.fields import fields as mafields
from .. import db, ma

query_ns = Namespace('query', description='query Resources')

responses_data_model = query_ns.model('responses_data_model', {'total': fields.Integer,
                                                               'items': fields.List(
                                                                   fields.Raw),
                                                               })
responses_format_model = query_ns.model('responses_format_model',
                                        {'code': fields.Integer,
                                         'key': fields.List(fields.String),
                                         'data': fields.Nested(responses_data_model)}
                                        )

query_list_patient_items_1 = query_ns.model('query_list_patient_items_1',
                                            {'patient_uid': UidFields(attribute='uid'),
                                             'patient_id': fields.String,
                                             'gender': fields.String,
                                             'age': fields.String,
                                             })
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

query_list_project_1 = query_ns.model('query_list_project_1', {'project_uid': UidFields(attribute='uid'),
                                                               'project_name': fields.String(attribute='name'),
                                                               })
query_list_project = query_ns.model('query_list_project', {'project_uid': UidFields(),
                                                           'project_name': fields.String,
                                                           })

query_list_project_series = query_ns.model('query_list_project_series_get', {'project_uid': UidFields(),
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


class PageSchema(ma.Schema):
    page = mafields.Integer(default=1)
    limit = mafields.Integer(default=20)
    sort = mafields.String(default='-uid')



class StudySchema(PageSchema):
    accession_number = mafields.String(default='')
    patient_id = mafields.String(default='')
    gender = mafields.String(default='')
    age = mafields.String(default='')
    study_date = mafields.DateTime(default='')
    study_description = mafields.String(default='')

    # fields.Int()
    # name = fields.Str()


page_schema = PageSchema()


def get_page_limit_sort(request):
    page_result = page_schema.dump(request.args, many=False)
    page = page_result['page']
    limit = page_result['limit']
    sort = page_result['sort']
    return page, limit, sort


@query_ns.route('/')
class QueryResources(Resource):
    def get(self, ):
        query = PatientModel.query
        patient_model:PatientModel = query.first()
        print(patient_model.study)
        print(patient_model.study[0].series)
        for series in patient_model.study[0].series:
            print(series.series_description)
            print(series.project[0].name)

        return 'QueryResources'


@query_ns.route('/list_patient')
class QueryPatientResources(Resource):
    series_resources = SeriesResources()
    study_resources = StudyResources()
    patient_resources = PatientResources()

    @query_ns.marshal_with(query_list_patient)
    def get(self, ):
        # page_result = page_schema.dump(request.args, many=False)
        # page = page_result['page']
        # limit = page_result['limit']
        page,limit,sort = get_page_limit_sort(request=request)

        order_by = sort[0]
        sort     = sort[1:]
        sort_column = getattr(PatientModel, sort)
        if order_by == '+':
            sort_column = sort_column.asc()
        else:
            sort_column = sort_column.desc()

        paginate = db.paginate(
            db.select(PatientModel).order_by(sort_column),
            page=page,
            per_page=limit
        )
        patient_model_list = paginate.items
        total = paginate.total
        response_list = []
        for patient_model in patient_model_list:
            response_list.append(self.patient_resources.get_age_by_patient(patient_model))

        result = query_ns.marshal(response_list,
                                  query_list_patient_items_1)
        jsonify_result = {'code': 2000,
                          'key': list(query_list_patient_items.keys()),
                          'data': {"total": total,
                                   "items": result}}
        return jsonify_result


@query_ns.route('/list_study')
class QueryStudyResources(Resource):
    series_resources = SeriesResources()
    study_resources = StudyResources()
    patient_resources = PatientResources()

    # @query_ns.marshal_with(query_list_study)
    def get(self, ):
        page, limit, sort = get_page_limit_sort(request=request)

        order_by = sort[0]
        sort = sort[1:]
        # sort_column = getattr(StudyModel, sort)
        # if order_by == '+':
        #     sort_column = sort_column.asc()
        # else:
        #     sort_column = sort_column.desc()

        # query = db.select(StudyModel).order_by(sort_column)
        query            = db.select(StudyModel)
        paginate         = db.paginate(query,page=page,per_page=limit)
        study_query_list = paginate.items
        total            = paginate.total
        # patient_uid_cache = dict()
        response_list = []
        for study_model in study_query_list:
            # patient_uid = study_model.patient.patient_id
            # if patient_uid in patient_uid_cache:
            #     patient_model = patient_uid_cache[patient_uid]
            # else:
            #     patient_model = PatientModel.query.filter_by(uid=patient_uid).first()
            #     patient_uid_cache[patient_model.uid] = patient_model

            study_dict = study_model.to_dict()
            study_dict['patient_id'] = study_model.patient.patient_id
            study_dict['gender'] = study_model.patient.gender
            study_dict['age'] = self.study_resources.get_age_by_study_date(birth_date=study_model.patient.birth_date,
                                                                           study_date=study_model.study_date)
            series_model_list = study_model.series
            for series_model in series_model_list:
                temp_dict = copy(study_dict)
                temp_dict['series_description'] = series_model.series_description
                temp_dict['series_uid'] = series_model.uid
                response_list.append(temp_dict)
        df = pd.json_normalize(response_list)
        df1 = df.pivot_table(index=['patient_id', 'study_date', 'gender', 'age',
                                    'study_description', 'accession_number'],
                             columns=['series_description'],
                             values=['series_uid'],
                             aggfunc='count', fill_value=0)
        print(order_by,sort,page,limit)

        df1.columns = df1.columns.get_level_values('series_description')
        df1.reset_index(inplace=True)
        jsonify_result = {'code': 2000,
                          'key': df1.columns.to_list(),
                          'data': {"total": total,
                                   "items": df1.to_dict(orient='records')}}
        # "items": orjson.loads(df1.to_json(orient='records'))}}
        return jsonify_result


@query_ns.route('/list_series')
class QuerySeriesResources(Resource):
    series_resources = SeriesResources()
    study_resources = StudyResources()
    patient_resources = PatientResources()

    @query_ns.marshal_with(query_list_series)
    def get(self, ):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        sort = request.args.get('sort', '-patients_id')
        paginate = db.paginate(
            db.select(SeriesModel).order_by(SeriesModel.series_date.asc()),
            page=page,
            per_page=limit
        )
        series_model_list = paginate.items
        response_list = self.get_series_dict_list_by_series_model_list(series_model_list=series_model_list)
        result = query_ns.marshal(response_list,
                                  query_list_series_items)
        df = pd.json_normalize(result)
        jsonify_result = {'code': 2000,
                          'key': df.columns.to_list(),
                          'data': {"total": paginate.total,
                                   "items": df.to_dict(orient='records')}}
        return jsonify_result

    def get_series_dict_list_by_series_model_list(self, series_model_list: List[PatientModel]):
        response_list = []
        for series_model in series_model_list:

            study       = series_model.study
            study_dict  = study.to_dict()
            age = self.study_resources.get_age_by_study_date(study.patient.birth_date,
                                                             study.study_date)
            series_dict = series_model.to_dict()
            series_dict['study_uid']         = study.uid
            series_dict['patient_id']        = study.patient.patient_id
            series_dict['gender']            = study.patient.gender
            series_dict['age']               = age
            series_dict['study_date']        = study_dict['study_date']
            series_dict['accession_number']  = study_dict['accession_number']
            series_dict['study_description'] = study_dict['study_description']
            response_list.append(series_dict)
        return response_list

    def get_series_dict_list_by_series_uid_list(self, series_uid_list: List[uuid.UUID]):
        series_model_list = SeriesModel.query.filter(SeriesModel.uid.in_(series_uid_list)).all()
        response_list = self.get_series_dict_list_by_series_model_list(series_model_list=series_model_list)
        return response_list


@query_ns.route('/list_project')
class QueryListProjectResources(Resource):
    def get(self, project_uid_str=None):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        sort = request.args.get('sort', '-patient_id')
        if project_uid_str:
            project_uid = uuid.UUID(project_uid_str)
            if not project_uid:
                return {'error': ' project not found'}, 404
            query = db.select(ProjectModel).filter_by(uid=project_uid).order_by(
                ProjectModel.name.desc())
        else:
            query = db.select(ProjectModel).order_by(ProjectModel.name.desc())

        paginate = db.paginate(query, page=page, per_page=limit)
        project_query = paginate.items
        total = paginate.total
        result = query_ns.marshal(project_query,
                                  query_list_project_1)
        df = pd.json_normalize(result)
        jsonify_result = {'code': 2000,
                          'key': df.columns.to_list(),
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')}}
        return jsonify_result


@query_ns.route('/list_project_series')
@query_ns.route('/list_project_series/<project_uid_str>')
class QueryListProjectSeriesResources(Resource):
    query_series_resources = QuerySeriesResources()
    study_resources = StudyResources()

    def get(self, project_uid_str=None):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        sort = request.args.get('sort', '-patient_id')
        if project_uid_str:
            project_uid = uuid.UUID(project_uid_str)
            project_model = ProjectModel.query.filter_by(uid=project_uid).first()
            if not project_model:
                return {'error': ' project not found'}, 404
            query = (db.select(StudyModel).filter(StudyModel.uid.in_(
                db.select(distinct(SeriesModel.study_uid)).join(ProjectSeriesModel,
                                                                SeriesModel.uid == ProjectSeriesModel.series_uid) \
                    .filter(ProjectSeriesModel.projects_uid == project_uid)))
                    .order_by(StudyModel.accession_number.desc()))
            paginate = db.paginate(query, page=page, per_page=limit)
            project_study_model_list = paginate.items
            total = paginate.total
            project_series_dict_list = []
            for study_model in project_study_model_list:
                series_dict_list = list(map(lambda series_model: series_model.to_dict(),
                                            study_model.series))
                for series_dict in series_dict_list:
                    study_dict = study_model.to_dict()
                    age = self.study_resources.get_age_by_study_date(study_model.patient.birth_date,
                                                                     study_model.study_date)
                    series_dict['study_uid'] = study_dict['uid']
                    series_dict['patient_id'] = study_model.patient.patient_id
                    series_dict['gender'] = study_model.patient.gender
                    series_dict['age'] = age
                    series_dict['study_date'] = study_dict['study_date']
                    series_dict['accession_number'] = study_dict['accession_number']
                    series_dict['study_description'] = study_dict['study_description']
                    project_series_dict_list.append(self.add_project_info(project_model, series_dict))
            result = query_ns.marshal(project_series_dict_list,
                                      query_list_project_series)
        else:
            project_model_list = ProjectModel.query.all()
            project_series_dict_list = []
            total = 0
            for project_model in project_model_list:
                start = time.time()
                query = db.select(StudyModel).filter(StudyModel.uid.in_(
                    db.select(distinct(SeriesModel.study_uid)).join(ProjectSeriesModel,
                                                          SeriesModel.uid == ProjectSeriesModel.series_uid) \
                      .filter(ProjectSeriesModel.projects_uid == project_model.uid)
                )).order_by(StudyModel.accession_number.desc())
                paginate = db.paginate(query,
                                       page=page,per_page=limit)


                project_study_model_list = paginate.items
                total                    = paginate.total + total
                for study_model in project_study_model_list:
                    series_dict_list = list(map(lambda series_model: series_model.to_dict(),
                                                study_model.series))
                    for series_dict in series_dict_list:
                        study_dict = study_model.to_dict()
                        age = self.study_resources.get_age_by_study_date(study_model.patient.birth_date,
                                                                         study_model.study_date)
                        series_dict['study_uid']  = study_dict['uid']
                        series_dict['patient_id'] = study_model.patient.patient_id
                        series_dict['gender']     = study_model.patient.gender
                        series_dict['age']        = age
                        series_dict['study_date'] = study_dict['study_date']
                        series_dict['accession_number'] = study_dict['accession_number']
                        series_dict['study_description'] = study_dict['study_description']
                        project_series_dict_list.append(self.add_project_info(project_model, series_dict))
                end = time.time()
            result = query_ns.marshal(project_series_dict_list,
                                      query_list_project_series)
        df = pd.json_normalize(result)

        df1 = df.pivot_table(index=['project_name',
                                    'patient_id', 'study_date', 'gender', 'age',
                                    'study_description', 'accession_number'],
                             columns=['series_description'],
                             values=['series_uid'],
                             aggfunc='count', fill_value=0)
        df1.columns = df1.columns.get_level_values('series_description')
        df1.reset_index(inplace=True)
        jsonify_result = {'code': 2000,
                          'key': df1.columns.to_list(),
                          'data': {"total": total,
                                   "items": df1.to_dict(orient='records')}}
        return jsonify_result

    def post(self, project_uid_str=None):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        sort = request.args.get('sort', '-patient_id')
        project_model_list = ProjectModel.query.all()
        project_series_dict_list = []
        for project_model in project_model_list:
            start = time.time()
            project_series_model_list = db.paginate(
                db.select(ProjectSeriesModel).filter_by(projects_uid=project_model.uid).order_by(
                    ProjectSeriesModel.uid.desc()),
                page=page,
                per_page=limit
            ).items
            series_uid_list = list(map(lambda project_series_model: project_series_model.series_uid,
                                       project_series_model_list))
            series_dict_list = self.query_series_resources.get_series_dict_list_by_series_uid_list(
                series_uid_list=series_uid_list)
            for series_dict in series_dict_list:
                project_series_dict_list.append(self.add_project_info(project_model, series_dict))
            end = time.time()
            print(project_model.name, (end - start), len(series_dict_list))
        result = query_ns.marshal(project_series_dict_list,
                                  query_list_project_series)
        df = pd.json_normalize(result)
        # print(df.columns)
        jsonify_result = {
                          'data': df.to_dict()}
        return jsonify_result

    def add_project_info(self, project_model: ProjectModel,
                         series_dict):
        series_dict['project_name'] = project_model.name
        series_dict['project_uid'] = project_model.uid.hex
        return series_dict


@query_ns.route('/list_study_text_report')
@query_ns.route('/list_study_text_report/<study_uid_str>')
class QueryListStudyTextReportResources(Resource):
    query_study_resources = QueryStudyResources()

    @query_ns.marshal_with(query_list_study_text_report)
    def get(self, study_uid_str=None):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        sort = request.args.get('sort', '-patient_id')
        miss = request.args.get('miss', None)
        if study_uid_str:
            study_uid = uuid.UUID(study_uid_str)
            study_model = StudyModel.query.filter_by(uid=study_uid).first()
            if not study_model:
                return {'error': ' project not found'}, 404
            text_report_model = TextReportModel.query.filter_by(study_uid=study_uid).first()
            if text_report_model:
                text = text_report_model.text
            else:
                text = ''
            study_dict = study_model.to_dict()
            study_dict['text'] = text
            result = query_ns.marshal(study_dict, query_list_study_text_report)
            total = 1
        else:
            if miss:
                query = db.select(StudyModel) \
                    .join(TextReportModel, StudyModel.uid == TextReportModel.study_uid,
                          isouter=True) \
                    .order_by(StudyModel.study_date.asc())
                paginate = db.paginate(query, page=page, per_page=limit)
            else:
                query = db.select(StudyModel) \
                    .join(TextReportModel, StudyModel.uid == TextReportModel.study_uid,
                          isouter=True) \
                    .filter(func.char_length(TextReportModel.text) > 0) \
                    .order_by(StudyModel.study_date.asc())

            paginate = db.paginate(query, page=page, per_page=limit)
            study_query = paginate.items
            total = paginate.total

            study_uid_list = list(map(lambda x: x.uid, study_query))
            study_text_report_dict_query = db.s3_session.execute(db.select(StudyModel, TextReportModel)
                                                                 .filter(StudyModel.uid.in_(study_uid_list))
                                                                 .join(TextReportModel,
                                                                    StudyModel.uid == TextReportModel.study_uid,
                                                                    isouter=True)
                                                                 .order_by(StudyModel.study_date.asc())).all()
            study_text_report_dict_list = []
            for i in range(len(study_text_report_dict_query)):
                study_dict = self.query_study_resources.study_resources.get_patient_info_by_study(
                    study_text_report_dict_query[i][0])
                if study_text_report_dict_query[i][1]:
                    text = study_text_report_dict_query[i][1].text
                else:
                    text = 'Na'
                study_dict['text'] = text
                study_text_report_dict_list.append(study_dict)

            result = query_ns.marshal(study_text_report_dict_list,
                                      query_list_study_text_report_items_1)
            # query_list_patient_items_1
        df = pd.json_normalize(result)
        jsonify_result = {'code': 2000,
                          'key': list(query_list_study_text_report_items.keys()),
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')}}
        return jsonify_result
