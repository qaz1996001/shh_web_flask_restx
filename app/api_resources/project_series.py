import io
import uuid
import calendar
import datetime
from typing import List

import pandas as pd
from flask import request, jsonify
from flask_sqlalchemy.query import Query
from flask_restx import Resource, fields, Namespace
from werkzeug.datastructures.file_storage import FileStorage
from sqlalchemy_filters import apply_filters
from app import db
from app.model import ProjectModel, ProjectSeriesModel, ProjectSeriesModel, seriesModel, SeriesModel, PatientModel
from app.schema import base as schema_base
# from app.schema.project_series import project_series_add_series_schema
from .base import UidFields


project_series_ns = Namespace('project_series',
                              description='project_series Resources')

@project_series_ns.route('/')
class ProjectSeriesResourcesTest(Resource):
    def get(self):
        return 'ProjectSeriesResourcesTest'



@project_series_ns.route('/series')
class ProjectSeriesAddSeriesResources(Resource):

    @project_series_ns.expect(post_project_series, validate=True)
    def post(self, ):
        return 'post ProjectSeriesResources'

    @project_series_ns.expect(post_project_series, validate=True)
    def delete(self, ):
        return 'delete ProjectSeriesResources'


# text/csv
# application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
# application/vnd.ms-excel
@project_series_ns.route('/upload')
class ProjectSeriesUploadResources(Resource):

    def post(self,):
        return 'post ProjectSeriesUploadResources'