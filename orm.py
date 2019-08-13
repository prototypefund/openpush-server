import enum
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"sqlite_autoincrement": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    clients = db.relationship("Client", back_populates="user")

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "clients": [c.as_dict() for c in self.clients],
        }

    def __repr__(self):
        return "<User %r>" % self.name


class Client(db.Model):
    __tablename__ = "client"
    __table_args__ = {"sqlite_autoincrement": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="clients")
    token = db.Column(db.String(80), nullable=False, unique=True)
    applications = db.relationship("Application", back_populates="client")

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "token": self.token,
            "applications": [a.as_dict() for a in self.applications],
        }

    def __repr__(self):
        return "<Client %r>" % self.name


class Application(db.Model):
    __tablename__ = "application"
    __table_args__ = {"sqlite_autoincrement": True}
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.String(80), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    client = db.relationship("Client", back_populates="applications")
    routing_token = db.Column(db.String(80), unique=True, nullable=False)

    def as_dict(self):
        return {
            "registration_id": self.registration_id,
            "routing_token": self.routing_token,
        }

    def __repr__(self):
        return "<Application %r>" % self.registration_id


class Priority(enum.Enum):
    HIGH = 1
    NORMAL = 2


class Message(db.Model):
    __tablename__ = "message"
    __table_args__ = {"sqlite_autoincrement": True}
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Enum(Priority), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_to_live = db.Column(db.Integer, nullable=False)
    collapse_key = db.Column(db.String(100))
    target_id = db.Column(db.Integer, db.ForeignKey("application.id"), nullable=False)
    target = db.relationship("Application")

    def as_dict(self):
        return {
            "subject": self.subject,
            "body": self.body,
            "priority": self.priority.name,
            "registration_id": self.target.registration_id,
        }

    def __repr__(self):
        return "<Message %r: %r>" % (self.subject, self.body)
