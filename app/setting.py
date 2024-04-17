import os
import pathlib

# 调试模式是否开启
DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS = False
# session必须要设置key
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# mysql数据库连接信息,这里改为自己的账号
# DATABASE = 'myweb.sqlite'
# SQLALCHEMY_DATABASE_URI = "sqlite:///" + \
#                           os.path.join(r"D:\00_Chen\Task08\shh_web\app", DATABASE)

# pgsql数据库连接信息,
# SQLALCHEMY_DATABASE_URI = "postgresql://postgres:pgpassword@127.0.0.1:5432/shh"
# sqlite
file_path = pathlib.Path(__file__)
db_path = file_path.parent.parent.joinpath('shh.db').absolute()
# db_path = file_path.parent.parent.joinpath('shh_test.db').absolute()
SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
print(SQLALCHEMY_DATABASE_URI)