from flask import jsonify
from orm import db, Client, Application
from connexion import NoContent
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


# user, injected by connexion auth handling is actually a client object here

def search(user):
    client = user
    return jsonify([a.as_dict() for a in Application.query.filter_by(client=client)])


def post(body, user):
    client = user
    name = body['name']
    while True:
        token = secrets.token_urlsafe(20)
        if not Application.query.filter_by(routing_token=token).one_or_none():
            break
    app = Application(name=name, client=client, routing_token=token)
    try:
        db.session.add(app)
        db.session.commit()
    except SQLAlchemyError as e:
        print(str(e))
        return NoContent, 400
    return jsonify(app.as_dict()), 201


def delete(id, user):
    client = user
    try:
        db.session.delete(Application.query.filter_by(id=id, client=client).one())
        db.session.commit()
    except NoResultFound:
        return NoContent, 404
    except SQLAlchemyError:
        return NoContent, 500
    return NoContent, 204
