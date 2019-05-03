#!/usr/bin/env python3

import connexion
from connexion.resolver import RestyResolver
from orm import db, User
from argon2 import PasswordHasher
from sqlalchemy.orm.exc import NoResultFound

app = connexion.App(__name__)
app.add_api('openapi.yml', resolver=RestyResolver('api'), strict_validation=True, validate_responses=True)
# due to using connexion the flask app is under app.app
app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.app.config['SQLALCHEMY_ECHO'] = True

if __name__ == '__main__':
    db.init_app(app.app)
    app.app.app_context().push()
    db.create_all()
    try:
        User.query.filter_by(name="admin").one()
    except NoResultFound:
        ph = PasswordHasher()
        user = User(name="admin", password=ph.hash("admin"))
        db.session.add(user)
        db.session.commit()
    app.run(debug=True)
