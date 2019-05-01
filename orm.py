from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    clients = db.relationship('Client', back_populates='user')

    def as_response(self):
        return {"id": self.id, "name": self.name}

    def __repr__(self):
        return '<User %r>' % self.username


class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='clients')
    applications = db.relationship('Application', back_populates='client')

    def __repr__(self):
        return '<Client %r>' % self.name


class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', back_populates='applications')
    routing_token = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Application %r>' % self.name


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    application = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    target_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    target = db.relationship('Application', back_populates=''
                                                           '')

    def __repr__(self):
        return '<Message %r: %r>' % (self.subject, self.body)
