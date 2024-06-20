import calendar
import datetime
import uuid
from typing import List

from flask import request, jsonify
from flask_restx import Resource, fields, Namespace
from .base import UidFields, Time
from .patient import PatientResources
from ..model import SeriesModel, StudyModel, PatientModel
from ..schema import page_schema
from .. import db

study_ns = Namespace('study', description='study Resources')
study_get_marshal = study_ns.model('study_get_marshal',
                                   {'study_uid': UidFields(attribute='uid'),
                                    'patient_uid': fields.String,
                                    'study_date': fields.String,
                                    'study_time': fields.String,
                                    'study_description': fields.String,
                                    'accession_number': fields.String,
                                    'orthanc_study_ID': fields.String,
                                    })

study_post_expect_items = study_ns.model('stydy_post_expect_items',
                                         dict(patient_id=fields.String,
                                              gender=fields.String,
                                              birth_date=fields.String,
                                              orthanc_patient_ID=fields.String,
                                              study_date=fields.Date,
                                              study_time=Time(default=datetime.time()),
                                              study_description=fields.String,
                                              accession_number=fields.String,
                                              orthanc_study_ID=fields.String))

study_post_expect = study_ns.model('study_post_expect',
                                   {'data_list': fields.List(fields.Nested(study_post_expect_items))})

study_post_marshal = study_ns.model('study_post_marshal',
                                    {'items': fields.List(fields.String)})

study_put_expect_items = study_ns.model('study_put_expect_items', dict(patient_uid=fields.String,
                                                                       study_date=fields.Date,
                                                                       study_time=Time(default=datetime.time()),
                                                                       study_description=fields.String,
                                                                       accession_number=fields.String,
                                                                       orthanc_patient_ID=fields.String))

study_put_expect = study_ns.model('study_post_expect',
                                  {'data_list': fields.List(fields.Nested(study_put_expect_items))})

study_put_marshal = study_ns.model('study_post_marshal',
                                   {'items': fields.List(fields.String)})

study_delete_expect_items = study_ns.model('study_delete_expect_items', dict(study_uid=fields.String,
                                                                             accession_number=fields.String))
study_delete_expect = study_ns.model('study_delete_expect',
                                     {'data_list': fields.List(fields.Nested(study_delete_expect_items))})


@study_ns.route('/<study_uid>')
class StudyResources(Resource):

    @study_ns.marshal_with(study_get_marshal)
    def get(self, study_uid=None):
        if study_uid:
            uid = uuid.UUID(study_uid)
            study_model = StudyModel.query.filter_by(uid=uid).first()
            if not study_model:
                return {'error': 'study not found'}, 404
            data_dict = self.get_patient_info_by_study(study_model)
            return data_dict, 200
        else:
            study_list = StudyModel.query.all()
            output = list(map(self.get_patient_info_by_study, study_list))
            return output, 200

    def put(self, study_uid=None):
        return 'StudyResources'

    def delete(self, study_uid=None):
        return 'StudyResources'

    def get_age_by_study_date(self, birth_date, study_date):
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
        return f'{year}Y{month}M'

    def get_patient_info_by_study(self, study: StudyModel):
        patient: PatientModel = PatientModel.query.filter_by(uid=study.patient_uid).first()
        age = self.get_age_by_study_date(birth_date=patient.birth_date,
                                         study_date=study.study_date)
        data_dict = study.to_dict()
        data_dict['age'] = age
        data_dict['patient_id'] = patient.patient_id
        data_dict['gender'] = patient.gender
        return data_dict

    def get_series_info_by_study(self, study: StudyModel):
        series_list: List[SeriesModel] = SeriesModel.query.filter_by(study_uid=study.uid).all()
        return series_list

    def add_study(self, patient_id,
                  gender,
                  birth_date,
                  study_date,
                  study_time,
                  study_description,
                  accession_number):

        patient = PatientModel.query.filter_by(patient_id=patient_id).first()

        if patient is None:
            patient = self.patient_resources.add_patient(patient_id=patient_id,
                                                         gender=gender,
                                                         birth_date=birth_date)
        study = StudyModel.query.filter_by(accession_number=accession_number).first()
        if study is None:
            study = StudyModel()
            study.patient_uid = patient.uid
            study_date_time = datetime.datetime.strptime(f'{study_date}{study_time}',
                                                         "%Y-%m-%d%H:%M:%S")
            study.study_date = study_date_time.date()
            study.study_time = study_date_time.time()
            study.study_description = study_description
            study.accession_number = accession_number
            study.created_at = datetime.datetime.now()
            db.session.add(study)
            db.session.commit()
            db.session.refresh(study)
            return study
        return None


@study_ns.route('/')
class StudiesResources(Resource):
    patient_resources = PatientResources()

    @study_ns.marshal_with(study_get_marshal)
    @study_ns.param('page', type=int)
    @study_ns.param('limit', type=int)
    @study_ns.param('sort', type=str)
    def get(self):
        page_result = page_schema.dump(request.args, many=False)
        query = db.select(StudyModel).filter(StudyModel.deleted_at.is_(None))
        paginate = db.paginate(query, page=page_result['page'], per_page=page_result['limit'])
        study_query_list = paginate.items
        total = paginate.total
        output = list(map(self.get_patient_info_by_study, study_query_list))
        return output

    @study_ns.expect(study_post_expect)
    def post(self):
        data_list = request.json['data_list']
        result_list = []
        if data_list:
            for data in data_list:
                patients_id = data.get('patient_id')
                gender = data.get('gender')
                birth_date = data.get('birth_date')
                study_date = data.get('study_date')
                study_time = data.get('study_time')
                study_description = data.get('study_description')
                accession_number = data.get('accession_number')
                if (patients_id and gender and birth_date and
                        study_date and study_time and study_description and accession_number):
                    result = self.add_study(patient_id=patients_id,
                                            gender=gender,
                                            birth_date=birth_date,
                                            study_date=study_date,
                                            study_time=study_time,
                                            study_description=study_description,
                                            accession_number=accession_number,)
                    if result:
                        result_list.append(result)
        response_list = list(map(lambda x: x.to_dict(), result_list))
        response = jsonify(response_list)
        response.status = 200
        return response

    @study_ns.expect(study_put_expect)
    def put(self):
        return 'StudyResources'

    @study_ns.expect(study_delete_expect)
    def delete(self):
        return 'StudyResources'

    def get_age_by_study_date(self, birth_date, study_date):
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
        return f'{year}Y{month}M'

    def get_patient_info_by_study(self, study: StudyModel):
        patient: PatientModel = PatientModel.query.filter_by(uid=study.patient_uid).first()
        age = self.get_age_by_study_date(birth_date=patient.birth_date,
                                         study_date=study.study_date)
        data_dict = study.to_dict()
        data_dict['age'] = age
        data_dict['patient_id'] = patient.patient_id
        data_dict['gender'] = patient.gender
        return data_dict

    def get_series_info_by_study(self, study: StudyModel):
        series_list: List[SeriesModel] = SeriesModel.query.filter_by(study_uid=study.uid).all()
        return series_list

    def add_study(self, patient_id,
                  gender,
                  birth_date,
                  study_date,
                  study_time,
                  study_description,
                  accession_number):

        patient = PatientModel.query.filter_by(patient_id=patient_id).first()

        if patient is None:
            patient = self.patient_resources.add_patient(patient_id=patient_id,
                                                         gender=gender,
                                                         birth_date=birth_date,
                                                         orthanc_patient_ID=None)
        study = StudyModel.query.filter_by(accession_number=accession_number).first()
        if study is None:
            study = StudyModel()
            study.patient_uid = patient.uid
            study_date_time = datetime.datetime.strptime(f'{study_date}{study_time}',
                                                         "%Y-%m-%d%H:%M:%S")
            study.study_date = study_date_time.date()
            study.study_time = study_date_time.time()
            study.study_description = study_description
            study.accession_number = accession_number
            study.created_at = datetime.datetime.now()
            db.session.add(study)
            db.session.commit()
            db.session.refresh(study)
        return study





# study_items_1 = study_ns.model('study_find_items_1',
#                                {'project_uid': UidFields(attribute='uid'),
#                                 'project_name': fields.String(attribute='name'), })
# study_items = study_ns.model('study_find_items',
#                              {'project_uid': UidFields(),
#                                     'project_name': fields.String, })

study_find_accession_number_post_expect = study_ns.model('study_find_post_expect',
                                                         {'accession_number_list':fields.List(fields.String)})
@study_ns.route('/find/accession_number')
class StudiesFindResources(Resource):
    # return study_get_marshal
    @study_ns.expect(study_find_accession_number_post_expect)
    def post(self):

        accession_number_list = request.json['accession_number_list']
        study_list = StudyModel.query.filter(StudyModel.accession_number.in_(accession_number_list)).all()

        response_list = []

        for study in study_list:
            patient = study.patient
            study_dict = study.to_dict()
            study_dict['patient_uid'] = patient.uid
            response_list.append(study_dict)
        result = study_ns.marshal(response_list, study_get_marshal)
        return result