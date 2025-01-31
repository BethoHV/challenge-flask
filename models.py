from app import db,app
from datetime import datetime

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

   session  = db.Column(db.String(50), nullable=False)     
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   valid = db.Column(db.Boolean)

   def __repr__(self):
      return '<UserSession %r>' % self.id
