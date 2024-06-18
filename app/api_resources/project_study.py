import io
import uuid
import calendar
import datetime
from typing import List, Dict

import pandas as pd
import sqlalchemy
from flask import request, jsonify,Response
from flask_sqlalchemy.query import Query
from flask_restx import Resource, fields, Namespace
from werkzeug.datastructures.file_storage import FileStorage
from sqlalchemy.dialects.postgresql import JSONB,NUMERIC,TEXT
from sqlalchemy import DOUBLE
from sqlalchemy import and_
from sqlalchemy.sql.expression import func,cast
from sqlalchemy_filters import apply_filters
from app import db
from app.model import ProjectModel, ProjectSeriesModel, ProjectStudyModel, StudyModel, SeriesModel, PatientModel
from app.schema import base as schema_base
from app.schema.project_study import project_study_add_study_schema
from .base import UidFields


project_study_ns = Namespace('project_study',
                             description='project_study Resources')

project_study_items = project_study_ns.model('project_study_items',
                                             {
                                                 'project_name': fields.String,
                                                 'patient_id': fields.String,
                                                 'gender': fields.String,
                                                 'age': fields.String,
                                                 'accession_number': fields.String,
                                                 'study_date': fields.String,
                                                 'study_description': fields.String,
                                                 # 'extra_data': fields.String,
                                             })

post_project_study = project_study_ns.model('post_project_study',
                                            {"project_uid": fields.String,
                                             "study_uid_list": fields.List(fields.String),})


file_upload_parser = project_study_ns.parser()
# file_upload_parser.add_argument('project_uid', type=str,location='form', required=True)
file_upload_parser.add_argument('file', type=FileStorage, location='files', required=True)

file_download_parser = project_study_ns.parser()
# file_download_parser.add_argument('project_uid', type=str,location='form')
file_download_parser.add_argument('project_name', type=str,location='form')
file_download_parser.add_argument('format', type=str,location='form')
# format


@project_study_ns.route('/')
class ProjectStudyResourcesTest(Resource):
    def get(self):
        return 'ProjectStudyResourcesTest'

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


def get_model_by_field(field_list):
    filter_field_list = list(filter(lambda x: field_model.get(x['field']) is not None, field_list))
    model_field_list = []
    for filter_field in filter_field_list:
        #  = list(map(lambda x: x['model'] = field_model.get(x['field'])) , filter_field_list))
        filter_field['model'] = field_model.get(filter_field['field'])
        model_field_list.append(filter_field)
    return model_field_list


@project_study_ns.route('/get_data')
class ProjectStudyGetDataResources(Resource):

    @project_study_ns.param('page', type=int, default='1')
    @project_study_ns.param('limit', type=int, default='20')
    @project_study_ns.param('sort', type=str)
    def post(self, ):
        print('request')
        print(request.json)
        print(request.args)
        page, limit, sort_column = schema_base.get_page_limit_sort(request=request, model=ProjectStudyModel)
        print(page, limit, sort_column)
        # query = ProjectStudyModel.query
        query: Query = db.session.query(ProjectStudyModel,StudyModel,PatientModel) \
            .join(StudyModel, ProjectStudyModel.study_uid == StudyModel.uid) \
            .join(PatientModel, StudyModel.patient_uid == PatientModel.uid)
        print(query)
        filter_ = schema_base.filter_schema.dump(request.json['filter_'], many=True)
        print('filter_', filter_)
        extra_data_filter = list(filter(lambda x:'extra_data.' in x['field'],filter_))
        extra_data_filter = list(map(self.convert_extra_data_filter_type, extra_data_filter))
        orther_filter = list(filter(lambda x: 'extra_data.' not in x['field'], filter_))

        print('extra_data_filter', extra_data_filter)
        print('orther_filter', orther_filter)
        orther_filter = get_model_by_field(orther_filter)
        extra_data_filter_sqlaichemy_not_na = list(map(lambda x: and_( ProjectStudyModel.extra_data.op("->>")(x['field']).op('!=')('Na')),
                                                       extra_data_filter))

        extra_data_filter_sqlaichemy = list(map(lambda x: and_(cast(ProjectStudyModel.extra_data.op("->")(x['field']),NUMERIC).op(x['op'])(x['value'])),
                                                extra_data_filter))
        # extra_data_filter = []
        extra_data_filter_sqlaichemy_not_na.insert(0,func.jsonb_typeof(ProjectStudyModel.extra_data) == sqlalchemy.text("\'object\'"))
        print('extra_data_filter', extra_data_filter)
        if filter_:
            filtered_query = apply_filters(query, orther_filter)
            filtered_query = filtered_query.filter(*extra_data_filter_sqlaichemy_not_na).filter(*extra_data_filter_sqlaichemy)
            # c = filtered_query.statement.compile(db.engine)
            # print(c.string)
            # print(c.params)
            # df_data = pd.read_sql(sql=c.string, con=db.engine, params=c.params)

            paginate = filtered_query.order_by(sort_column).paginate(page=page,
                                                                     per_page=limit)
            print('filtered_query', filtered_query)
        else:
            paginate = query.order_by(sort_column).paginate(page=page,
                                                            per_page=limit)
        # c = filtered_query.statement.compile(db.engine)
        # print(c.string)
        # print(c.params)
        total = paginate.total
        print('total',total)
        list_project_study_result = paginate.items
        response_list = list(map(self.add_info, list_project_study_result))
        df: pd.DataFrame = pd.json_normalize(response_list)

        columns = df.columns.to_list()
        group_key  = schema_base.get_group_key_by_series(columns)
        group_key.update(self.get_extra_data_key(columns=columns))

        # columns = list(map(lambda x: x.replace('extra_data.', ''), columns))
        df.columns = columns
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": df.to_dict(orient='records')},
                          'group_key': group_key,
                          'op_list': schema_base.filter_op_list}
        return jsonify(jsonify_result)

    def add_info(self, item: sqlalchemy.engine.row.Row):
        project_study = item[0]
        study = project_study.study
        study_dict = {'project_study_uid' : project_study.uid,
                      'project_name'      : project_study.project.name
                      }
        study_dict['patient_id'] = study.patient.patient_id
        study_dict['gender'] = study.patient.gender
        study_dict['age'] = get_age_by_study_date(study.patient.birth_date, study.study_date)
        study_dict.update(study.to_dict_view())
        study_dict['extra_data'] = project_study.extra_data
        return study_dict

    def get_extra_data_key(self,columns: List[str]):
        extra_data_key_list = list(filter(lambda x: 'extra_data' in x, columns))
        # extra_data_key_list = list(map(lambda x: x.replace('extra_data.', ''), extra_data_key_list))
        return {"extra_data_keys": extra_data_key_list}

    def convert_extra_data_filter_type(self,extra_data_filter: Dict):
        new_extra_data_filter = extra_data_filter.copy()
        new_extra_data_filter['field'] = new_extra_data_filter['field'].replace('extra_data.','')
        try:
            new_value = float(new_extra_data_filter['value'])
            new_extra_data_filter['value'] = new_value
        except ValueError :
            pass
        return new_extra_data_filter


@project_study_ns.route('/study')
class ProjectStudyAddStudyResources(Resource):

    @project_study_ns.expect(post_project_study, validate=True)
    def post(self, ):
        data = project_study_add_study_schema.load(request.json)
        # data.project_uid
        print(data)
        project_model = ProjectModel.query.filter_by(uid=data['project_uid']).first()
        if project_model:
            for study_uid in data['study_uid_list']:
                study_model = StudyModel.query.filter_by(uid=study_uid).first()
                if study_model:
                    project_study_model = ProjectStudyModel.query.filter_by(study_uid=study_model.uid,
                                                                            project_uid=project_model.uid,).first()
                    if project_study_model:
                        continue
                    else:
                        datetime_now = datetime.datetime.now()
                        project_study_model = ProjectStudyModel(study_uid=study_model.uid,
                                                                project_uid=project_model.uid,
                                                                extra_data = {},
                                                                created_at = datetime_now)
                        db.session.add(project_study_model)
                else:
                    continue
            db.session.commit()
            return jsonify({'code': 2000,})
        else:
            import sqlalchemy
            return jsonify({'code': 400,})
        # project_uid = request.json['project_uid']
        # study_uid_list = request.json['study_uid_list']

    @project_study_ns.expect(post_project_study, validate=True)
    def delete(self, ):
        return 'delete ProjectStudyResources'


# text/csv
# application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
# application/vnd.ms-excel
@project_study_ns.route('/upload/excel')
class ProjectStudyUploadExcelResources(Resource):

    # @project_study_ns.expect(file_upload_parser)
    # def post(self,):
    #     data = file_upload_parser.parse_args()
    #     print(data)
    #     project_uid       = data['project_uid']
    #     file: FileStorage = data['file']
    #     print(file.mimetype)
    #     print(file.filename)
    #     file_obj = io.BytesIO()
    #     file.save(file_obj)
    #     file_obj.seek(0)
    #     df = pd.read_excel(file_obj,dtype={'patient_id':str,
    #                                        'accession_number':str,
    #                                        'study_date':str,
    #                                        })
    #     df['study_date'] = pd.to_datetime(df['study_date'])
    #     print(df.columns)
    #
    #     query_data:Query = db.session.query(
    #                                    ProjectStudyModel.uid.label('project_study_uid'),
    #                                    ProjectStudyModel.project_uid.label('project_uid'),
    #                                    ProjectStudyModel.study_uid.label('study_uid'),
    #                                    PatientModel.patient_id.label('patient_id'),
    #                                    StudyModel.study_date.label('study_date'),) \
    #                             .join(StudyModel,ProjectStudyModel.study_uid == StudyModel.uid) \
    #                             .join(PatientModel, StudyModel.patient_uid == PatientModel.uid) \
    #                             .filter(ProjectStudyModel.project_uid == project_uid)
    #     c = query_data.statement.compile(db.engine)
    #     df_data = pd.read_sql(sql=c.string, con=db.engine, params=c.params)
    #     df_data['study_date'] = pd.to_datetime(df_data['study_date'])
    #     df_temp = pd.merge(df_data,df,left_on =['project_study_uid'] #left_on =['patient_id','study_date']
    #                                  ,right_on=['project_study_uid'] #right_on=['patient_id','study_date']
    #                                  ,how='inner')
    #     df_temp.fillna('Na',inplace=True)
    #     print(df_temp)
    #     project_study_uid_list = df_temp['project_study_uid'].to_list()
    #     project_study_model_list:List[ProjectStudyModel] = ProjectStudyModel.query.filter(ProjectStudyModel.uid.in_(project_study_uid_list)).all()
    #     for project_study_model in project_study_model_list:
    #         project_study_uid = project_study_model.uid
    #         temp_data = df_temp[df_temp['project_study_uid'] == project_study_uid]
    #         new_extra_data = temp_data.iloc()[0,5:].to_dict()
    #         print('new_extra_data')
    #         print(new_extra_data)
    #         print('project_study_model.extra_data')
    #         print(project_study_model.extra_data,type(project_study_model.extra_data))
    #         if project_study_model.extra_data:
    #             project_study_model.extra_data.update(new_extra_data)
    #         else:
    #             project_study_model.extra_data = new_extra_data
    #         print('new_extra_data',new_extra_data)
    #     db.session.commit()
    #     # for index,row in df_temp.iterrows():
    #     #     project_study_uid = row['project_study_uid']
    #     #     print(project_study_uid)
    #     #     project_study_model:ProjectStudyModel = ProjectStudyModel.query.filter(ProjectStudyModel.uid ==project_study_uid).first()
    #     #     project_study_model.extra_data = row.iloc()[11:-2].to_dict()
    #     #     project_study_model.updated_at = datetime.datetime.now()
    #     #     # print(row.iloc()[11:].to_dict())
    #     #     # print(project_study_model)
    #     #     db.session.commit()
    #     #     break
    #
    #     return df.columns.to_list()
    @project_study_ns.expect(file_upload_parser)
    def post(self, ):
        data = file_upload_parser.parse_args()
        print(data)
        file: FileStorage = data['file']
        print(file.mimetype)
        print(file.filename)
        file_obj = io.BytesIO()
        file.save(file_obj)
        file_obj.seek(0)
        df = pd.read_excel(file_obj, dtype={'patient_id': str,
                                            'accession_number': str,
                                            'study_date': str,
                                            })
        df['study_date'] = pd.to_datetime(df['study_date'])
        df['project_study_uid'] = df['project_study_uid'].map(lambda x: uuid.UUID(x))
        project_study_uid_list = df['project_study_uid'].to_list()
        project_study_model_list: List[ProjectStudyModel] = ProjectStudyModel.query.filter(ProjectStudyModel.uid.in_(project_study_uid_list)).all()
        for project_study_model in project_study_model_list:
            project_study_uid = project_study_model.uid
            temp_data = df[df['project_study_uid'] == project_study_uid]
            new_extra_data = temp_data.iloc()[0, 6:].to_dict()
            if project_study_model.extra_data:
                new_extra_data.update(project_study_model.extra_data)
                project_study_model.extra_data = new_extra_data
            else:
                project_study_model.extra_data = new_extra_data
            project_study_model.updated_at = datetime.datetime.now()
        db.session.commit()
        return df.columns.to_list()


@project_study_ns.route('/download')
class ProjectStudyDownloadResources(Resource):

    @project_study_ns.expect(file_download_parser)
    def post(self,):
        data = file_download_parser.parse_args()
        project_name = data['project_name']
        format = data['format']
        project_model = ProjectModel.query.filter_by(name=project_name).first()
        print(data)
        print(project_model)
        if project_model:
            project_uid = project_model.uid
            query_data:Query = db.session.query(
                                           ProjectStudyModel.uid.label('project_study_uid'),
                                           ProjectStudyModel.project_uid.label('project_uid'),
                                           ProjectStudyModel.study_uid.label('study_uid'),
                                           PatientModel.patient_id.label('patient_id'),
                                           StudyModel.study_date.label('study_date'),
                                           StudyModel.accession_number.label('accession_number'), ) \
                                    .join(StudyModel,ProjectStudyModel.study_uid == StudyModel.uid) \
                                    .join(PatientModel, StudyModel.patient_uid == PatientModel.uid) \
                                    .filter(ProjectStudyModel.project_uid == project_uid)
            c = query_data.statement.compile(db.engine)
            df_data = pd.read_sql(sql=c.string, con=db.engine, params=c.params)
            print(df_data.columns)
            if 'xlsx' == format or 'excel' == format :
                file_obj = io.BytesIO()
                df_data.to_excel(file_obj, index=False)
                file_obj.seek(0)
                return Response(
                    file_obj.read(),
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={"Content-Disposition": f"attachment;filename=project_study.xlsx"}
                )
            elif 'csv' == format :
                return jsonify(df_data.to_csv(index=False))
            elif 'json' == format :
                return jsonify(df_data.to_dict('records'))
            else:
                return jsonify(df_data.to_dict('records'))


def get_age_by_study_date(birth_date, study_date):
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

