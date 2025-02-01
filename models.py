from functools import wraps
import string
import random
from flask import jsonify, request
from app import db
from datetime import datetime

#função midware para validar auth do usuario
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get('Authorization')

        #passando e pegando user_id por formrequest
        user_id = request.form.get('user_id')

        if not auth_token:
            return jsonify({"error": "Autorização necessária"}), 401

        token_session = auth_token.replace("Bearer ", "")
        session = UserSession.query.filter_by(user_id=user_id, session=token_session,valid=True).first()
       
        if not session:
            return jsonify({"error": "Sessão inválida ou expirada"}), 401

        return f(*args, **kwargs)  # Continua se autenticado

    return decorated_function

#função para gerar token randomido para session  
def rand_str():
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(6))

class User(db.Model):
   __tablename__ = 'user'
   id = db.Column(db.Integer, primary_key=True)     
   username = db.Column(db.String(20), nullable=False)     
   password = db.Column(db.String(80), nullable=False)     
   fullname = db.Column(db.String(50), nullable=False)     
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   active = db.Column(db.Boolean, default=True)

   user_session = db.relationship("UserSession", backref='user')

   def __repr__(self):
      return '<User %r>' % self.id

class UserSession(db.Model):
   __tablename__ = 'user_session'
   id = db.Column(db.Integer, primary_key=True)     
   user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)    
   session  = db.Column(db.String(50), unique=True, nullable=False, default=rand_str)     
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   valid = db.Column(db.Boolean)

   def __repr__(self):
      return '<UserSession %r>' % self.id
   
class Category(db.Model):
   __tablename__ = 'category'
   id = db.Column(db.Integer, primary_key=True)     
   name = db.Column(db.String(20), nullable=False)     
   description  = db.Column(db.String(50), nullable=False) 
   order = db.Column(db.Integer)       
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   deleted = db.Column(db.Boolean,default=False)
   category_product = db.relationship("Product", backref='category')

   def __repr__(self):
      return '<Category %r>' % self.id

class Product(db.Model):
   __tablename__ = 'product'
   id = db.Column(db.Integer, primary_key=True)     
   name = db.Column(db.String(20), nullable=False)     
   description  = db.Column(db.String(50), nullable=False) 
   order = db.Column(db.Integer)       
   price = db.Column(db.Integer)
   category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)  
   deleted = db.Column(db.Boolean,default=False)

   def __repr__(self):
      return '<Product %r>' % self.id