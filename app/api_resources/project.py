import uuid
from datetime import datetime

from flask import request
from flask_restx import Resource, fields, Namespace

from app import db
from app.api_resources.base import UidFields
from app.model import ProjectModel, ProjectSeriesModel, ListProjectStudyModel

project_ns = Namespace('project', description='Project Resources')
project_get = project_ns.model('project_get',
                               dict(project_uid=UidFields(attribute='uid'),
                                    project_name=fields.String(attribute='name'),
                                    ))


@project_ns.route('/<project_uid>')
class ProjectResources(Resource):
    @project_ns.marshal_with(project_get)
    def get(self, project_uid=None):
        if project_uid:
            uid = uuid.UUID(project_uid)
            project_model = ProjectModel.query.filter_by(uid=uid).first()
            if not project_model:
                return {'error': 'project not found'}, 404
            return project_model.to_dict()
        else:
            patient_list = ProjectModel.query.all()
            output = list(map(lambda project_model: project_model.to_dict(), patient_list))
            return output

    def put(self, project_uid=None):
        # query step
        name = request.args.get('name')
        if project_uid:
            uid = uuid.UUID(project_uid)
            project_model: ProjectModel = ProjectModel.query.filter_by(uid=uid).first()
            if not project_model:
                return {'error': 'project not found'}, 404
            (db.s3_session.query(ProjectModel).filter_by(uid=project_model.uid)
               .update(dict(name=name)))
            (db.s3_session.query(ListProjectStudyModel).filter_by(project_name=project_model.uid)
               .update(dict(project_name=name)))

            db.s3_session.commit()
            return {'message': 'Project update'}
        else:
            return {'error': 'No project specified'}, 404

    def delete(self, project_uid=None):
        # query step
        if project_uid:
            uid = uuid.UUID(project_uid)
            project_model: ProjectModel = ProjectModel.query.filter_by(uid=uid).first()
            if not project_model:
                return {'error': 'project not found'}, 404
            db.s3_session.query(ProjectSeriesModel).filter_by(projects_uid=project_model.uid).delete()
            db.s3_session.query(ListProjectStudyModel).filter_by(project_uid=project_model.uid).delete()
            db.s3_session.query(ProjectModel).filter_by(uid=project_model.uid).delete()
            db.s3_session.commit()
            return {'message': 'Project deleted'}
        else:
            return {'error': 'No project specified'}, 404


@project_ns.route('/')
class ProjectsResources(Resource):
    @project_ns.marshal_with(project_get)
    def get(self, ):
        patient_list = ProjectModel.query.all()
        output = list(map(lambda project_model: project_model.to_dict(), patient_list))
        return output

    @project_ns.param('name', type=str)
    def post(self, ):
        name = request.args.get('name')
        project_model = ProjectModel.query.filter_by(name=name).first()
        print(project_model)
        if not project_model:
            project_model = ProjectModel()
            project_model.name = name
            db.session.add(project_model)
            db.session.commit()
            db.session.refresh(project_model)
            # db.relationship()
            return {'data': project_model.to_dict()}, 201
        else:
            return {'error': 'project name already exists'}, 400
