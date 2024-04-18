import calendar
import datetime
import uuid
from flask import request
from flask_restx import Resource, fields, Namespace
# from ..model import PatientModel
from .. import db

file_ns = Namespace('file', description='File Resources')



@file_ns.route('/')
class FileResources(Resource):
    @file_ns.param('page', type=int, default=1)
    @file_ns.param('limit', type=int, default=20)
    @file_ns.param('sort', type=str, default='+uid')
    def get(self):
        return 'FileResources'


    def post(self):
        return 'FileResources'


    def put(self):
        return 'FileResources'


    def delete(self):
        return 'FileResources'