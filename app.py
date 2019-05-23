#!/usr/bin/env python3

import connexion
from connexion.resolver import RestyResolver
from flask.helpers import get_debug_flag
from sqlalchemy.orm.exc import NoResultFound

import configs
from orm import db, User


def create_app(config_object=configs.ProdConfig):
    app = connexion.App(__name__)
    app.add_api("openapi.yml", resolver=RestyResolver("api"), strict_validation=True)
    app.app.config.from_object(config_object)
    db.init_app(app.app)
    app.app.app_context().push()
    db.create_all()
    return app


def flask_app():
    """Returns an acutal flask app for using 'flask shell'"""
    return create_app().app


if __name__ == "__main__":
    CONFIG = configs.DevConfig if get_debug_flag() else configs.ProdConfig
    app = create_app(CONFIG)
    if CONFIG.USER and CONFIG.PASS:
        try:
            User.query.filter_by(name=CONFIG.USER).one()
        except NoResultFound:
            from argon2 import PasswordHasher

            ph = PasswordHasher()
            user = User(name=CONFIG.USER, password=ph.hash(CONFIG.PASS))
            db.session.add(user)
            db.session.commit()

    app.run(port=CONFIG.APP_PORT, debug=CONFIG.DEBUG)
