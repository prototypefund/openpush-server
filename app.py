#!/usr/bin/env python3

import connexion
from connexion.resolver import RestyResolver
from orm import db, User
from sqlalchemy.orm.exc import NoResultFound

connexion_app = connexion.App(__name__)
connexion_app.add_api('openapi.yml', resolver=RestyResolver('api'), strict_validation=True)
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if __name__ == '__main__':
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    try:
        User.query.filter_by(name="admin").one()
    except NoResultFound:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        user = User(name="admin", password=ph.hash("admin"))
        db.session.add(user)
        db.session.commit()
    connexion_app.run(debug=True, threaded=True)
