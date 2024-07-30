import uuid
from datetime import datetime

import pandas as pd
from flask import request, jsonify
from flask_restx import Resource, fields, Namespace

from app import db
from app.api_resources.base import UidFields
from app.model import ProjectModel, ProjectSeriesModel, ListProjectStudyModel, ProjectStudyModel
from app.schema import base as base_schema
from app.schema import project as project_schema
project_ns = Namespace('project', description='Project Resources')

responses_data_model = project_ns.model('responses_data_model',
                                        base_schema.responses_data_model)
responses_format_model = project_ns.model('responses_format_model',
                                          base_schema.responses_format_model)

project_get = project_ns.model('project_get',
                               project_schema.project_get)

project_items_1 = project_ns.model('project_items_1',
                                   project_schema.project_items_1)
project_items = project_ns.model('project_items',
                                 {'project_uid': UidFields(), 'project_name': fields.String, })
project_data = project_ns.clone('project_data',
                                responses_data_model,
                                {'items': fields.List(
                                    fields.Nested(project_items))})

projec_list = project_ns.clone('projec_list',
                               responses_format_model,
                               {'data': fields.Nested(project_data)})


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
            (db.session.query(ProjectModel).filter_by(uid=project_model.uid)
             .update(dict(name=name)))
            (db.session.query(ListProjectStudyModel).filter_by(project_name=project_model.uid)
             .update(dict(project_name=name)))

            db.session.commit()
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

            db.session.query(ProjectSeriesModel).filter_by(project_uid=project_model.uid).delete()
            db.session.query(ProjectStudyModel).filter_by(project_uid=project_model.uid).delete()
            db.session.query(ListProjectStudyModel).filter_by(project_uid=project_model.uid).delete()
            db.session.query(ProjectModel).filter_by(uid=project_model.uid).delete()
            db.session.commit()
            return {'message': 'Project deleted'}
        else:
            return {'error': 'No project specified'}, 404


@project_ns.route('/')
class ProjectsResources(Resource):
    #@project_ns.marshal_with(projec_list)
    def get(self,):
        query = ProjectModel.query
        paginate = query.paginate(page=1, per_page=20)
        list_project_result = paginate.items
        total = paginate.total
        response_list = list(map(lambda x: x.to_dict(), list_project_result))
        df: pd.DataFrame = pd.json_normalize(response_list)
        columns = list(project_items.keys())
        items = project_ns.marshal(df.to_dict(orient='records'),
                                   project_items_1)
        jsonify_result = {'code': 2000,
                          'key': columns,
                          'data': {"total": total,
                                   "items": items},
                          }
        #print(df)
        return jsonify(jsonify_result)

    @project_ns.param('name', type=str)
    def post(self, ):
        name = request.args.get('name')
        project_model = ProjectModel.query.filter_by(name=name).first()
        if project_model is None:
            project_model = ProjectModel()
            project_model.name = name
            project_model.created_at = datetime.now()
            db.session.add(project_model)
            db.session.commit()
            db.session.refresh(project_model)
            # db.relationship()
            return {'data': project_model.to_dict()}, 201
        else:
            return {'error': 'project name already exists'}, 400


