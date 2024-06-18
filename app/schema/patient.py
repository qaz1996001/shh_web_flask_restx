from flask_marshmallow.fields import fields as mafields
from .. import ma


class PatientPostItemsSchema(ma.Schema):
    patient_id = mafields.String()
    gender = mafields.String()
    birth_date = mafields.Date(format = '%Y-%m-%d')
    orthanc_patient_ID = mafields.String()


patient_post_items_schema = PatientPostItemsSchema()
