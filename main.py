import os
import sys

# DON\\\\\\\\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from flask_cors import CORS

# استيراد blueprint التداول مباشرة من trading.py
from trading import trading_bp

app = Flask(__name__)
app.config[\\\\'SECRET_KEY\\\\] = \\\\'asdf#FGSgvasgfSSSWGT\\\\' 

# تمكين CORS للسماح بالطلبات من الواجهة الأمامية
CORS(app)

# تسجيل blueprint التداول
app.register_blueprint(trading_bp, url_prefix=\\\\'/api/trading\\\\])

# uncomment if you need to use database
# app.config[\\\\'SQLALCHEMY_DATABASE_URI\\\\] = f\\\"sqlite:///{os.path.join(os.path.dirname(__file__), \\\\'database\\\\] , \\\\'app.db\\\\])}\\\"
# app.config[\\\\'SQLALCHEMY_TRACK_MODIFICATIONS\\\\] = False
# db.init_app(app)
# with app.app_context():
#     db.create_all()

if __name__ == \\\\'__main__\\\\]:
    app.run(host=\\\\'0.0.0.0\\\\] , port=5000, debug=True)
