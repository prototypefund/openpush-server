from flask import jsonify
from connexion import NoContent
from orm import db, User
import sqlalchemy


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
    return jsonify([user.as_response() for user in User.query.all()])


def post(body):
    name = body['name']
    password = body['password']
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    user = User(name=name, password=ph.hash(password))
    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError:
        return NoContent, 400
    return jsonify(User.query.filter_by(name=name).one().as_response()), 201


def update(id, body):
    return NoContent, 200


def get(id):
    try:
        return jsonify(User.query.filter_by(id=id).one().as_response())
    except sqlalchemy.orm.exc.NoResultFound:
        return NoContent, 404
    except sqlalchemy.exc.SQLAlchemyError:
        return NoContent, 500


def delete(id):
    try:
        db.session.delete(User.query.filter_by(id=id).one())
        db.session.commit()
    except sqlalchemy.orm.exc.NoResultFound:
        return NoContent, 404
    except sqlalchemy.exc.SQLAlchemyError:
        return NoContent, 500
    return NoContent, 204
