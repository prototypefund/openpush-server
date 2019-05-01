#!/usr/bin/env python3

import connexion
from connexion.resolver import RestyResolver
from orm import db

app = connexion.App(__name__)
app.add_api('openapi.yml', resolver=RestyResolver('api'), strict_validation=True, validate_responses=True)
# due to using connexion the flask app is under app.app
app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

if __name__ == '__main__':
    db.init_app(app.app)
    app.app.app_context().push()
    db.create_all()
    app.run(debug=True)
