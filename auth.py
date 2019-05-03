from orm import db, User


def basic_auth(username, password, required_scopes=None):
    import argon2
    ph = argon2.PasswordHasher()
    try:
        ph.verify(User.query.filter_by(name=username).one().password, password)
    except argon2.exceptions.VerifyMismatchError:
        return None
    return {'sub': username}


def apikey_auth(apiKey, required_scopes=None):
    return {'sub': "tbd"}
