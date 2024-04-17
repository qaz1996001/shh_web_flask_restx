from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from .flask_orjson import OrjsonProvider

# 創建專案對象
app: Flask = Flask(__name__)
app.json = OrjsonProvider(app)
app.config.from_object('app.setting')  # 模組下的setting檔案名，不用加py尾碼
# app.config.from_envvar('FLASKR_SETTINGS')  # 環境變數，指向設定檔setting的路徑
# 創建資料庫物件
db = SQLAlchemy()
db.init_app(app)
# CORS
cors = CORS(app)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Marshmallow
ma = Marshmallow(app)

from .api_resources import api_blueprint

app.register_blueprint(api_blueprint)


@app.route('/')
def hello():
    return "Hello, MVC框架!", 200


@app.route('/create_db')
def create_db():
    db.create_all()
    # BaseModel.metadata.create_all(db.engine)
    return "create_db", 200


@app.route('/del_db')
def del_db():
    db.drop_all()
    return "del_db", 200

