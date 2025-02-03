from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)

#set config do redis
redis_cache= redis.Redis(host='localhost',port='6379',db=0)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///challenge.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from models import *
from routes import *

with app.app_context():
        db.create_all()
    
if __name__ == "__main__":
        app.run(debug=True)