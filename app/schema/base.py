import re
from flask_restx import Resource, fields, Namespace
from flask_marshmallow.fields import fields as mafields

from .. import ma




class PageSchema(ma.Schema):
    page = mafields.Integer(default=1)
    limit = mafields.Integer(default=20)
    sort = mafields.String(default='-uid')


class FilterSchema(ma.Schema):
    field = mafields.String()
    op = mafields.String()
    value = mafields.String()



class AccessionNumberSchema(ma.Schema):
    accession_number_list = mafields.List(mafields.String(required=True), required=True)

page_schema = PageSchema()
filter_schema = FilterSchema()
accession_number_schema = AccessionNumberSchema()


filter_op_list = [
    #'is_null',
    'like',
    '==',
    '>', '<',
    '>=', '<=', '!=',
    'regexp',
    'is_not_null', 'in',
    #'not_in',
    #'ilike', 'not_ilike',
    #'any', 'not_any'
]


# use map
def op_like_add_percent(x):
    if x['op'] == 'like':
        if x['value'].startswith('%') or x['value'].endswith('%'):
            pass
        else:
            x['value'] = rf"%{x['value']}%"
    return x


# use filter
def get_orther_filter(x):
    if (x['field'] != 'impression_str') and (x['op'] != 'regexp'):
        return True
    elif x['op'] == 'regexp':
        return False
    elif x['field'] == 'impression_str':
        return False
    return True


def get_regexp_filter(x):
    if x['op'] == 'regexp':
        return True
    return False


def get_regexp(regexp_filter_list, model):
    regexp_list = []
    for i in regexp_filter_list:
        column = getattr(model, i['field'])
        regexp_list.append(column.regexp_match(i['value'],flags = 'i'))
    return regexp_list


def get_page_limit_sort(request, model, default=None):
    page_result = page_schema.dump(request.args, many=False)
    page = page_result['page']
    limit = page_result['limit']

    if request.args.get('sort'):
        sort = page_result['sort']
    else:
        sort = default
    order_by = sort[0]
    sort = sort[1:]
    sort_column = getattr(model, sort)
    if order_by == '+':
        sort_column = sort_column.asc()
    else:
        sort_column = sort_column.desc()
    return page, limit, sort_column


def get_query_filter(request):
    filter_dict = filter_schema.dump(request.args)
    if filter_dict:
        return [filter_dict]
    else:
        return None



########## for group_key ##############################
series_structure_sort = {
    "ADC": 100,
    "DWI0": 110,
    "DWI1000": 120,
    'T1_AXI': 300,
    'T1_COR': 311,
    'T1_SAG': 312,
    'T1CE_AXI': 320,
    'T1CE_COR': 321,
    'T1CE_SAG': 323,
    'T1FLAIR_AXI': 331,
    'T1FLAIR_COR': 332,
    'T1FLAIR_SAG': 333,
    'T1FLAIRCE_AXI': 341,
    'T1FLAIRCE_COR': 342,
    'T1FLAIRCE_SAG': 343,
    'T1CUBE_AXI': 350,
    'T1CUBE_COR': 351,
    'T1CUBE_SAG': 352,
    'T1CUBE_AXIr': 355,
    'T1CUBE_CORr': 356,
    'T1CUBE_SAGr': 357,
    'T1CUBECE_AXI': 361,
    'T1CUBECE_COR': 362,
    'T1CUBECE_SAG': 363,
    'T1CUBECE_AXIr': 365,
    'T1CUBECE_CORr': 366,
    'T1CUBECE_SAGr': 367,
    'T1FLAIRCUBE_AXI': 370,
    'T1FLAIRCUBE_COR': 371,
    'T1FLAIRCUBE_SAG': 372,
    'T1FLAIRCUBE_AXIr': 375,
    'T1FLAIRCUBE_CORr': 376,
    'T1FLAIRCUBE_SAGr': 377,
    'T1FLAIRCUBECE_AXI': 380,
    'T1FLAIRCUBECE_COR': 381,
    'T1FLAIRCUBECE_SAG': 382,
    'T1FLAIRCUBECE_AXIr': 385,
    'T1FLAIRCUBECE_CORr': 386,
    'T1FLAIRCUBECE_SAGr': 387,
    'T1BRAVO_AXI': 390,
    'T1BRAVO_COR': 391,
    'T1BRAVO_SAG': 392,
    'T1BRAVO_AXIr': 395,
    'T1BRAVO_CORr': 396,
    'T1BRAVO_SAGr': 397,
    'T1BRAVOCE_AXI': 400,
    'T1BRAVOCE_COR': 401,
    'T1BRAVOCE_SAG': 402,
    'T1BRAVOCE_AXIr': 405,
    'T1BRAVOCE_CORr': 406,
    'T1BRAVOCE_SAGr': 407,
    'T2_AXI': 410,
    'T2_COR': 411,
    'T2_SAG': 412,
    'T2CE_AXI': 420,
    'T2CE_COR': 421,
    'T2CE_SAG': 423,
    'T2FLAIR_AXI': 431,
    'T2FLAIR_COR': 432,
    'T2FLAIR_SAG': 433,
    'T2FLAIRCE_AXI': 441,
    'T2FLAIRCE_COR': 442,
    'T2FLAIRCE_SAG': 443,
    'T2CUBE_AXI': 450,
    'T2CUBE_COR': 451,
    'T2CUBE_SAG': 452,
    'T2CUBE_AXIr': 455,
    'T2CUBE_CORr': 456,
    'T2CUBE_SAGr': 457,
    'T2CUBECE_AXI': 461,
    'T2CUBECE_COR': 462,
    'T2CUBECE_SAG': 463,
    'T2CUBECE_AXIr': 465,
    'T2CUBECE_CORr': 466,
    'T2CUBECE_SAGr': 467,
    'T2FLAIRCUBE_AXI': 470,
    'T2FLAIRCUBE_COR': 471,
    'T2FLAIRCUBE_SAG': 472,
    'T2FLAIRCUBE_AXIr': 475,
    'T2FLAIRCUBE_CORr': 476,
    'T2FLAIRCUBE_SAGr': 477,
    'T2FLAIRCUBECE_AXI': 480,
    'T2FLAIRCUBECE_COR': 481,
    'T2FLAIRCUBECE_SAG': 482,
    'T2FLAIRCUBECE_AXIr': 485,
    'T2FLAIRCUBECE_CORr': 486,
    'T2FLAIRCUBECE_SAGr': 487,
    'T2BRAVO_AXI': 490,
    'T2BRAVO_COR': 491,
    'T2BRAVO_SAG': 492,
    'T2BRAVO_AXIr': 495,
    'T2BRAVO_CORr': 496,
    'T2BRAVO_SAGr': 497,
    'T2BRAVOCE_AXI': 500,
    'T2BRAVOCE_COR': 501,
    'T2BRAVOCE_SAG': 502,
    'T2BRAVOCE_AXIr': 505,
    'T2BRAVOCE_CORr': 506,
    'T2BRAVOCE_SAGr': 507,
}
series_general_pattern = re.compile(
    ('project_name|patient_id|gender|age|study_date|study_time|study_description|accession_number'))
series_structure_pattern = re.compile(('T1|T2|DWI|ADC'))
series_special_pattern = re.compile(('MRA|SWAN|eSWAN'))
series_perfusion_pattern = re.compile(('DSC|ASL'))
series_functional_pattern = re.compile(('RESTING|CVR|DTI'))
series_general_sort = {
    'project_name':95,
    'patient_id': 100,
    'gender': 110,
    'age': 120,
    'study_date': 130,
    'study_time': 140,
    'study_description': 150,
    'accession_number': 160,
    'series_description': 170
}
series_special_sort = {
    'MRA_BRAIN': 100,
    'MRA_NECK': 110,
    'MRAVR_BRAIN': 120,
    'MRAVR_NECK': 130,
    'SWAN': 200,
    'SWANmIP': 210,
    'SWANPHASE': 210,
    'eSWAN': 300,
    'eSWANmIP': 310,
    'eSWANPHASE': 330,
}
series_perfusion_sort = {
    'ASLSEQ': 100,
    'ASLSEQATT': 110,
    'ASLSEQATT_COLOR': 111,
    'ASLSEQCBF': 120,
    'ASLSEQCBF_COLOR': 121,
    'ASLPROD': 130,
    'ASLPRODCBF': 140,
    'ASLPRODCBF_COLOR': 141,
    'ASLSEQPW': 150,
    'DSC': 200,
    'DSCCBF_COLOR': 210,
    'DSCCBV_COLOR': 220,
    'DSCMTT_COLOR': 230,

}
series_functional_sort = {
    'RESTING': 100,
    'RESTING2000': 101,
    'CVR': 200,
    'CVR1000': 201,
    'CVR2000': 202,
    'CVR2000_EAR': 203,
    'CVR2000_EYE': 204,
    'DTI32D': 300,
    'DTI64D': 330
}


def get_group_key_by_series(columns):
    return dict(
        general_keys=sorted(filter(lambda x: series_general_pattern.match(x) is not None, columns),
                            key=lambda x: series_general_sort.get(x, 999)),
        structure_keys=sorted(filter(lambda x: series_structure_pattern.match(x) is not None, columns),
                              key=lambda x: series_structure_sort.get(x, 999)),
        special_keys=sorted(filter(lambda x: series_special_pattern.match(x) is not None, columns),
                            key=lambda x: series_special_sort.get(x, 999)),
        perfusion_keys=sorted(filter(lambda x: series_perfusion_pattern.match(x) is not None, columns),
                              key=lambda x: series_perfusion_sort.get(x, 999)),
        functional_keys=sorted(filter(lambda x: series_functional_pattern.match(x) is not None, columns),
                               key=lambda x: series_functional_sort.get(x, 999))
    )



class UidFields(fields.Raw):
    __schema_type__ = "string"

    def format(self, value):
        if isinstance(value, uuid.UUID):
            return value.hex
        elif isinstance(value, str):
            return value
        else:
            return value


responses_data_model = {'total': fields.Integer,
                        'items': fields.List(fields.Raw),}
responses_format_model = {'code': fields.Integer,
                          'key': fields.List(fields.String),
                          'data': fields.Nested(responses_data_model)}
