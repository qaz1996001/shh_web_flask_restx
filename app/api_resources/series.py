import calendar
import datetime
import uuid

from flask import jsonify, request
from flask_restx import Resource, fields, Namespace
# from .base import UidFields
# from .patient import PatientResources
from .study import StudiesResources
from ..model import StudyModel, PatientModel, SeriesModel
from .. import db

series_ns = Namespace('series', description='series Resources')


@series_ns.route('/')
class SeriesResources(Resource):
    study_resources = StudiesResources()

    def get(self, ):
        series_list = SeriesModel.query.all()
        output = list(map(lambda series: series.to_dict(), series_list))
        return jsonify(output)

    def post(self, ):
        data_list = request.json['data_list']
        result_list = []
        if data_list:
            for data in data_list:
                patients_id = data.get('patients_id')
                gender = data.get('gender')
                birth_date = data.get('birth_date')
                study_date = data.get('studies_date')
                study_time = data.get('studies_time')
                study_description = data.get('studies_description')
                accession_number = data.get('accession_number')
                series_date = data.get('series_date')
                series_time = data.get('series_time')
                series_description = data.get('series_description')
                modality = data.get('modality')
                if (patients_id and gender and birth_date and
                        study_date and study_time and study_description and accession_number and
                        series_date and series_time and series_description and modality):
                    result = self.add_series(patient_id=patients_id,
                                             gender=gender,
                                             birth_date=birth_date,
                                             study_date=study_date,
                                             study_time=study_time,
                                             study_description=study_description,
                                             accession_number=accession_number,
                                             series_date=series_date,
                                             series_time=series_time,
                                             series_description=series_description,
                                             modality=modality)
                    if result:
                        result_list.append(result)
        response_list = list(map(lambda x: x.to_dict(), result_list))
        response = jsonify(response_list)
        if len(response_list) > 0:
            response.status = 201
            return response
        else:
            response.status = 200
            return response

    def put(self, ):
        return 'SeriesResources'

    def delete(self, ):
        return 'SeriesResources'

    def get_series_info(self, series: SeriesModel):
        study = StudyModel.query.filter_by(uid=series.study_uid).first()
        patient = PatientModel.query.filter_by(uid=study.patients_uid).first()
        age = self.study_resources.get_age_by_study_date(birth_date=patient.birth_date,
                                                         study_date=study.study_date)
        study_date = study.study_date.strftime("%Y%m%d")
        data_dict = series.to_dict()
        data_dict['age'] = age
        data_dict['patients_id'] = patient.patients_id
        data_dict['gender'] = patient.gender
        data_dict['study_date'] = study.study_date
        data_dict['study_description'] = study.study_description
        data_dict['accession_number'] = study.accession_number
        data_dict[
            'id'] = f"{patient.patients_id}_{study_date}_{data_dict['modality']}_{data_dict['accession_number']}"
        return data_dict

    def add_series(self, patient_id, gender, birth_date,
                   study_date, study_time, study_description, accession_number,
                   series_date, series_time, series_description, modality):
        study = StudyModel.query.filter_by(accession_number=accession_number).first()
        if study is None:
            study = self.study_resources.add_study(patient_id=patient_id, gender=gender,
                                                   birth_date=birth_date, study_date=study_date,
                                                   study_time=study_time,
                                                   study_description=study_description,
                                                   accession_number=accession_number)
        series = SeriesModel.query.filter_by(study_uid=study.uid,
                                             series_description=series_description,
                                             modality=modality
                                             ).first()
        if series is None:
            series = SeriesModel()
            series.study_uid = study.uid
            study_date_time = datetime.datetime.strptime(f'{series_date}{series_time}',
                                                           "%Y%m%d%H%M%S")
            series.series_date = study_date_time.date()
            series.series_time = study_date_time.time()
            series.series_description = series_description
            series.modality = modality
            series.created_at = datetime.datetime.now()
            db.s3_session.add(series)
            db.s3_session.commit()
            db.s3_session.refresh(series)
            return series
        return None


@series_ns.route('/<series_ns_uid>')
class SeriesOneResources(Resource):
    def get(self, series_uid=None):
        uid = uuid.UUID(series_uid)
        series_model = PatientModel.query.filter_by(uid=uid).first()
        if not series_model:
            return {'error': 'study not found'}, 404
        data_dict = self.get_series_info(series_model)
        return data_dict, 200

    def put(self, series_uid=None):
        return 'SeriesResources'

    def delete(self, series_uid=None):
        return 'SeriesResources'

    def get_series_info(self, series: SeriesModel):
        study = StudyModel.query.filter_by(uid=series.study_uid).first()
        patient = PatientModel.query.filter_by(uid=study.patient_uid).first()
        age = self.study_resources.get_age_by_study_date(birth_date=patient.birth_date,
                                                         study_date=study.study_date)
        study_date = study.study_date.strftime("%Y%m%d")
        data_dict = series.to_dict()
        data_dict['age'] = age
        data_dict['patient_id'] = patient.patient_id
        data_dict['gender'] = patient.gender
        data_dict['study_date'] = study.study_date
        data_dict['study_description'] = study.study_description
        data_dict['accession_number'] = study.accession_number
        data_dict[
            'id'] = f"{patient.patient_id}_{study_date}_{data_dict['modality']}_{data_dict['accession_number']}"
        return data_dict
