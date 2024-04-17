import calendar
import datetime
import uuid
from sqlalchemy.sql.expression import func
from flask import request
from flask_restx import Resource, fields, Namespace
from ..model import PatientModel
from .. import db
from .base import UidFields
from ..schema import page_schema, patient_post_items_schema

patient_ns = Namespace('patient', description='Patient Resources')
patient_get_marshal_itmes = patient_ns.model('patient_get_marshal_itmes', dict(patient_uid=UidFields(attribute='uid'),
                                                                               patient_id=fields.String,
                                                                               gender=fields.String,
                                                                               age=fields.String,
                                                                               orthanc_patient_ID=fields.String))
patient_get_marshal = patient_ns.model('patient_get_marshal',
                                       {'items': fields.List(fields.Nested(patient_get_marshal_itmes))})

patient_post_expect_items = patient_ns.model('patient_post_expect_items', dict(patient_id=fields.String,
                                                                               gender=fields.String,
                                                                               birth_date=fields.Date,
                                                                               orthanc_patient_ID=fields.String))

patient_post_expect = patient_ns.model('patient_post_expect',
                                       {'data_list': fields.List(fields.Nested(patient_post_expect_items))})

patient_post_marshal = patient_ns.model('patient_post_marshal',
                                        {'items': fields.List(fields.String)})

patient_put_expect_items = patient_ns.model('patient_put_expect_items', dict(patient_id=fields.String,
                                                                             gender=fields.String,
                                                                             birth_date=fields.Date,
                                                                             orthanc_patient_ID=fields.String))

patient_put_expect = patient_ns.model('patient_put_expect',
                                      {'data_list': fields.List(fields.Nested(patient_put_expect_items))})

patient_delete_expect_items = patient_ns.model('patient_delete_expect_items', dict(patient_uid=fields.String,
                                                                                   patient_id=fields.String))

patient_delete_expect = patient_ns.model('patient_delete_expect',
                                         {'data_list': fields.List(fields.Nested(patient_delete_expect_items))})


@patient_ns.route('/<patient_uid>')
class PatientResources(Resource):
    # @patient_ns.response(200, 'Success')
    # @patient_ns.response(400, 'Validation Error')
    @patient_ns.marshal_with(patient_get_marshal_itmes)
    def get(self, patient_uid=None):
        if patient_uid:
            uid = uuid.UUID(patient_uid)
            patient_model = PatientModel.query.filter_by(uid=uid).first()
            if not patient_model:
                return {'error': 'patient not found'}, 404
            data_dict = self.get_age_by_patient(patient_model)
            return data_dict
        return {}


    @patient_ns.expect(patient_put_expect_items)
    def put(self, patient_uid=None):
        return 'PatientResources'

    def delete(self, patient_uid=None):
        return 'PatientResources'

    def add_patient(self, patient_id, gender, birth_date, orthanc_patient_ID):
        # patient_model
        patient_model = PatientModel.query.filter_by(patient_id=patient_id).first()
        if patient_model is None:
            patient_model = PatientModel()
            patient_model.patient_id = patient_id
            patient_model.gender = gender
            birth_date_obj = datetime.datetime.strptime(birth_date, "%Y%m%d")
            patient_model.birth_date = birth_date_obj
            patient_model.orthanc_patient_ID = orthanc_patient_ID
            patient_model.created_at = datetime.datetime.now()
            db.session.add(patient_model)
            db.session.commit()
            db.session.refresh(patient_model)
            return patient_model
        return None
    @staticmethod
    def get_age_by_patient(patient: PatientModel):
        birth_date = patient.birth_date
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
        data_dict = patient.to_dict()
        data_dict['age'] = f'{year}Y{month}M'
        return data_dict


@patient_ns.route('/')
class PatientsResources(Resource):
    # @patient_ns.response(200, 'Success')
    # @patient_ns.response(400, 'Validation Error')
    @patient_ns.marshal_with(patient_get_marshal)
    @patient_ns.param('page', type=int)
    @patient_ns.param('limit', type=int)
    @patient_ns.param('sort', type=str)
    def get(self):
        page_result = page_schema.dump(request.args, many=False)
        query = db.select(PatientModel).filter(PatientModel.deleted_at.is_(None))
        paginate = db.paginate(query, page=page_result['page'], per_page=page_result['limit'])
        patient_query_list = paginate.items
        total = paginate.total
        output = list(map(self.get_age_by_patient, patient_query_list))
        return {'items': output}

    @patient_ns.expect(patient_post_expect)
    @patient_ns.marshal_with(patient_post_marshal)
    def post(self):
        data = patient_ns.payload
        patient_post_items_schema_list = patient_post_items_schema.load(data=data['data_list'],
                                                                        many=True,
                                                                        unknown='exclude')
        result_list = []
        for data in patient_post_items_schema_list:
            patient_id = data.get('patient_id')
            gender = data.get('gender')
            birth_date = data.get('birth_date')
            orthanc_patient_ID = data.get('orthanc_patient_ID')
            result = self.add_patient(patient_id, gender, birth_date, orthanc_patient_ID)
            if result:
                result_list.append(result.uid.hex)
        return {"items": result_list}

    @patient_ns.expect(patient_put_expect)
    def put(self):
        return 'PatientResources'

    @patient_ns.expect(patient_delete_expect)
    def delete(self):
        return 'PatientResources'

    def add_patient(self, patient_id, gender, birth_date, orthanc_patient_ID):
        # patient_model
        patient_model = PatientModel.query.filter_by(patient_id=patient_id,
                                                     gender = gender,
                                                     birth_date=birth_date).first()
        if patient_model is None:
            patient_model = PatientModel()
            patient_model.patient_id = patient_id
            patient_model.gender = gender
            patient_model.birth_date = birth_date
            patient_model.orthanc_patient_ID = orthanc_patient_ID
            patient_model.created_at = datetime.datetime.now()
            db.session.add(patient_model)
            db.session.commit()
            db.session.refresh(patient_model)
        return patient_model

    @staticmethod
    def get_age_by_patient(patient: PatientModel):
        birth_date = patient.birth_date
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
        data_dict = patient.to_dict()
        data_dict['age'] = f'{year}Y{month}M'
        return data_dict
