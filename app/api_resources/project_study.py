import uuid
from datetime import datetime

from flask import request
from flask_restx import Resource, fields, Namespace

from app import db
from app.api_resources.base import UidFields
from app.model import ProjectModel, ProjectSeriesModel, ListProjectStudyModel, ProjectStudyModel

project_study_ns = Namespace('project_study',
                             description='project_study Resources')


@project_study_ns.route('/')
class ProjectStudyResourcesTest(Resource):
    def get(self):
        return 'ProjectStudyResourcesTest'


@project_study_ns.route('/get_data')
class ProjectStudyResources(Resource):
    def get(self, ):
        return 'get ProjectStudyResources'

    @project_study_ns.param('page', type=int, default='1')
    @project_study_ns.param('limit', type=int, default='20')
    @project_study_ns.param('sort', type=str)
    def post(self, ):
        return 'post ProjectStudyResources'

    def delete(self, ):
        return 'delete ProjectStudyResources'
