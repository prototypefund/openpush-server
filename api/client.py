from flask import jsonify
from connexion import NoContent
from orm import db, User, Client
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
import secrets

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


def search(user):
    return jsonify([client.as_dict() for client in Client.query.join(Client.user).filter(User.name == user)])


def post(body, user):
    name = body['name']
    userobj = User.query.filter_by(name=user).one()
    while True:
        token = secrets.token_urlsafe(20)
        if not Client.query.filter_by(token=token).one_or_none():
            break
    client = Client(name=name, user=userobj, token=token)
    try:
        db.session.add(client)
        db.session.commit()
    except SQLAlchemyError as e:
        print(str(e))
        return NoContent, 400
    return jsonify(client.as_dict()), 201


def put(id, body, user):
    name = body['name']
    try:
        client = Client.query.join(Client.user).filter(Client.id == id, User.name == user).one()
    except NoResultFound:
        return NoContent, 404
    client.name = name
    db.session.commit()
    return jsonify(client.as_dict()), 200


def delete(id, user):
    try:
        db.session.delete(Client.query.join(Client.user).filter(Client.id == id, User.name == user).one())
        db.session.commit()
    except NoResultFound:
        return NoContent, 404
    except SQLAlchemyError:
        return NoContent, 500
    return NoContent, 204
