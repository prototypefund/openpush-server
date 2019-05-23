import flask
from connexion import NoContent
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from orm import db, User


# Using connexion automatic routing
# paths:
#  /:
#    get:
#       # Implied operationId: api.get
#  /foo:
#    get:
#       # Implied operationId: api.foo.search
#    post:
#       # Implied operationId: api.foo.post
#
#  '/foo/{id}':
#    get:
#       # Implied operationId: api.foo.get
#    put:
#       # Implied operationId: api.foo.put
#    copy:
#       # Implied operationId: api.foo.copy
#    delete:
#       # Implied operationId: api.foo.delete


def search():
    return jsonify([user.as_dict() for user in User.query.all()])


def post(body):
    name = body["name"]
    password = body["password"]
    from argon2 import PasswordHasher

    ph = PasswordHasher()
    user = User(name=name, password=ph.hash(password))
    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError:
        return NoContent, 400
    return jsonify(User.query.filter_by(name=name).one().as_dict()), 201


def update(id, body):
    name = body["name"]
    password = body["password"]
    try:
        user = User.query.filter_by(id=id).one()
    except NoResultFound:
        return NoContent, 404
    from argon2 import PasswordHasher

    ph = PasswordHasher()
    user.password = ph.hash(password)
    user.name = name
    db.session.commit()
    return jsonify(user.as_dict()), 200


def get(id):
    try:
        return jsonify(User.query.filter_by(id=id).one().as_dict())
    except NoResultFound:
        return NoContent, 404
    except SQLAlchemyError:
        return NoContent, 500


def delete(id):
    user = User.query.get(id)
    if not user:
        return NoContent, 404
    try:
        db.session.delete(user)
        db.session.commit()
    except SQLAlchemyError as e:
        print(str(e))
        return NoContent, 500
    response = flask.make_response("", 204)
    response.headers = {"Content-Length": 0}
    return response
