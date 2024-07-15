import re

import pandas as pd
from flask import jsonify, request
from flask_restx import Resource, Namespace,fields
from sqlalchemy import and_
from sqlalchemy_filters import apply_filters
from flask_marshmallow.fields import fields as mafields
from ..model import TextReportRawModel,OnePageReportModel

from app.schema import base as base_schema
from app.schema import project_study as project_study_schema

text_report_ns = Namespace('text_report', description='text report Resources')


post_text_report = text_report_ns.model('post_text_report',
                                            {"accession_number_list": fields.List(fields.String),})


@text_report_ns.route('/find')
class TextReportResources(Resource):
    @text_report_ns.param('patient_id', type=str, default='00189626')
    @text_report_ns.param('accession_number', type=str, default='20806070002')
    def get(self):
        patient_id = request.args.get('patient_id')
        accession_number = request.args.get('accession_number')
        query = OnePageReportModel.query.filter(and_(OnePageReportModel.id == accession_number,
                                                     OnePageReportModel.chr_no == patient_id)).first()
        if query is None:
            return jsonify({'error': 'No such accession number.'}), 404

        return query.to_dict()

    # @text_report_ns.route('/find/accession')


@text_report_ns.route('/find/accession')
class TextReportAccessionResources(Resource):

    @text_report_ns.expect(post_text_report)
    def post(self):
        data = base_schema.accession_number_schema.load(request.json)
        accession_number_list = data['accession_number_list']
        text_report_model_list = OnePageReportModel.query.filter((OnePageReportModel.id.in_(accession_number_list))).all()
        response_list = list(map(lambda x: x.to_dict(), text_report_model_list))
        if data is None:
            return jsonify({'error': 'No such accession number.'}), 404
        return response_list

