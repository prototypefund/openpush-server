#!/usr/bin/env python3

from flask import Flask, jsonify
import connexion
from connexion.resolver import RestyResolver
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = connexion.App(__name__)
app.add_api('openapi.yml', resolver=RestyResolver('api'))
# due to using connexion the flask app is under app.app
app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app.app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    application = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/')
def hello_world():
    return jsonify(message='Hello, World!')

if __name__ == '__main__':
    app.run(debug=True)
