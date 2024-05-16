from flask_restx import Api, Resource
from .. import app

from flask import Blueprint

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
# 創建API物件
api = Api(api_blueprint, version='2.0', title='SHH API',
          description='A sample API', doc='/doc/'
          )

from .patient import patient_ns
from .study import study_ns
from .series import series_ns
from .project import project_ns
from .project_study import project_study_ns
from .text_report import text_report_ns
from .query import query_ns
from .query_v2 import query_ns as v2query_ns
from .file import file_ns

api.add_namespace(ns=patient_ns ,path='/patient')
api.add_namespace(ns=study_ns   ,path='/study')
api.add_namespace(ns=text_report_ns  ,path='/text_report')
api.add_namespace(ns=series_ns  ,path='/series')
api.add_namespace(ns=project_ns ,path='/project')
api.add_namespace(ns=project_study_ns ,path='/project_study/')
api.add_namespace(ns=query_ns   ,path='/query')
api.add_namespace(ns=v2query_ns   ,path='/query/v2')
api.add_namespace(ns=file_ns ,path='/file')
