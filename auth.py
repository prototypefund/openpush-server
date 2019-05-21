from orm import User, Client, Application
from sqlalchemy.orm.exc import NoResultFound


def basic_auth(username, password, required_scopes=None):
    import argon2

    ph = argon2.PasswordHasher()
    try:
        user = User.query.filter_by(name=username).one()
        ph.verify(user.password, password)
    except (argon2.exceptions.VerifyMismatchError, NoResultFound):
        return None
    return {"sub": user}


def clientkey_auth(apiKey, required_scopes=None):
    try:
        client = Client.query.filter_by(token=apiKey).one()
    except NoResultFound:
        return None
    return {"sub": client}


def routing_token_auth(apiKey, required_scopes=None):
    try:
        app = Application.query.filter_by(routing_token=apiKey).one()
    except NoResultFound:
        return None
    return {"sub": app}
