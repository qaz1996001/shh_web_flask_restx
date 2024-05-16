import calendar
import datetime
import io
import re
import uuid

import flask
import flask_restx
from flask import request,Response
import urllib.parse

from flask_restx import Resource, fields, Namespace
from werkzeug.datastructures.file_storage import FileStorage
from .. import s3_session, s3_client, OBJECT_BUCKET_NAME

from .query_v2 import filter_list_study_text_report
from ..model import PatientModel, FileModel
from .. import db

file_ns = Namespace('file', description='File Resources')

# file_meta_data = """
#     'series_uid': str,
#     'file_name': str,
#     'file_size': str,
#     'file_datetime': str,
#     'file_type': str,
#     'file_status': str,
#     'file_url': str,
#
# """

file_meta_data = file_ns.model('file_meta_data',
                               {
                                   'series_uid': fields.String(attribute='series_uid'),
                                   'file_name': fields.String(attribute='file_name'),
                                   'file_size': fields.String(attribute='file_size'),
                                   'file_datetime': fields.String(attribute='file_datetime'),
                                   'file_type': fields.String(attribute='file_type'),
                                   'file_status': fields.String(attribute='file_status'),
                                   'file_url': fields.String(attribute='file_url'),
                               })
file_upload_parser = file_ns.parser()
file_upload_parser.add_argument('series_uid', type=str, )
# parser.add_argument('series_uid', type=str,location='form')
# parser.add_argument('file_name', type=str,location='form')
# parser.add_argument('file_size', type=str,location='form')
# parser.add_argument('file_datetime', type=str,location='form')
# parser.add_argument('file_type', type=str,location='form')
# parser.add_argument('file_status', type=str,location='form')
file_upload_parser.add_argument('file_url', type=str, location='form')
file_upload_parser.add_argument('file', type=FileStorage, location='files')

# file_download_parser = file_ns.parser()
# file_upload_parser.add_argument('file_url', type=str, location='')


@file_ns.route('/')
class FileResources(Resource):
    info_pattern = re.compile('(\d{8})_(\d{8})_(MR|CT)_(\w*)')

    @file_ns.param('page', type=int, default=1)
    @file_ns.param('limit', type=int, default=20)
    @file_ns.param('sort', type=str, default='+uid')
    def get(self):
        return 'FileResources'

    @file_ns.expect(file_upload_parser)
    def post(self):
        data = file_upload_parser.parse_args()
        file_url = data['file_url']
        file = data['file']
        file_obj = io.BytesIO()
        file.save(file_obj)
        file_obj.seek(0)
        response = s3_client.put_object(Body=file_obj.read(),
                                        Bucket=OBJECT_BUCKET_NAME,
                                        Key=file_url)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            s3_obj_response = s3_client.get_object(Bucket=OBJECT_BUCKET_NAME, Key=file_url)
            file_name = file_url.split('/')[-1]
            file_size = s3_obj_response['ContentLength']
            file_datetime = s3_obj_response['LastModified']

            # file_type = file_url.split('/')[-1]
            # result = self.info_pattern.match(file_url).groups()
            file_model = FileModel.query.filter_by(file_url=file_url).first()
            if file_model is None:
                file_model = FileModel()
            # file_model.series_uid = data['series_uid']
            file_model.file_name = file_name
            file_model.file_size = file_size
            file_model.file_datetime = file_datetime
            file_model.file_url = file_url
            db.session.add(file_model)
            db.session.commit()
            return 'OK', 200

        return 'FileResources'

    def put(self):
        return 'FileResources'

    def delete(self):
        return 'FileResources'

    @staticmethod
    def parse_study_info(file_url: str):

        # file_url_list = file_url.split('/')

        file_name = file_url.split('/')[-1]
        pass

@file_ns.route('/download/<file_url>')
class FileDownloadResources(Resource):
    def get(self, file_url=None):
        if file_url is None:
            return flask.abort(404)
        Key = urllib.parse.unquote(file_url)
        print(file_url)
        print(Key)

        response = s3_client.get_object(Bucket=OBJECT_BUCKET_NAME, Key=Key)
        file_name = Key.split('/')[-1]
        print(response)
        return Response(
            response['Body'].read(),
            mimetype=response['ContentType'],
            headers={"Content-Disposition": f"attachment;filename={file_name}"}
        )
