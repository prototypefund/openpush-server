#!/usr/bin/env python3

import connexion
from connexion.resolver import RestyResolver
from orm import db
import configs
from flask.helpers import get_debug_flag


def create_app(config_object=configs.ProdConfig):
    app = connexion.App(__name__)
    app.add_api('openapi.yml', resolver=RestyResolver('api'), strict_validation=True)
    app.app.config.from_object(config_object)
    db.init_app(app.app)
    app.app.app_context().push()
    db.create_all()
    return app


def flask_app():
    """Returns an acutal flask app for using 'flask shell'"""
    return create_app().app


if __name__ == '__main__':
    CONFIG = configs.DevConfig if get_debug_flag() else configs.ProdConfig
    app = create_app(CONFIG)
    app.run(port=CONFIG.APP_PORT, debug=CONFIG.DEBUG)