from flask_restx import Api, Resource
from .. import app

from flask import Blueprint

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
# 創建API物件
api = Api(api_blueprint, version='1.0', title='SHH API',
          description='A sample API', doc='/doc/'
          )

from .patient import patient_ns
from .study import study_ns
from .series import series_ns
from .project import project_ns
from .query import query_ns
from .query_v2 import query_ns as v2query_ns

api.add_namespace(ns=patient_ns ,path='/patient')

api.add_namespace(ns=study_ns   ,path='/study')
api.add_namespace(ns=series_ns  ,path='/series')
api.add_namespace(ns=project_ns ,path='/project')
api.add_namespace(ns=query_ns   ,path='/query')
api.add_namespace(ns=v2query_ns   ,path='/query/v2')

