import pytest
import webtest
from pytest_localserver.http import WSGIServer

from app import create_app
from configs import TestConfig
from orm import User, Client, Application, Message
from orm import db as _db


@pytest.fixture(scope="class")
def app():
    _app = create_app(TestConfig)
    ctx = _app.app.test_request_context()
    ctx.push()

    yield _app.app

    ctx.pop()


@pytest.fixture(scope="class")
def testapp(app):
    """A Webtest app."""
    return webtest.TestApp(app)


@pytest.fixture(scope="class", autouse=True)
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    setup_initial_data(_db)

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def testserver(request, app):
    server = WSGIServer(application=app)
    server.start()
    request.addfinalizer(server.stop)
    return server


def setup_initial_data(db):
    from argon2 import PasswordHasher

    ph = PasswordHasher()
    u1 = User(name="User 1", password=ph.hash("password1"))
    u2 = User(name="User 2", password=ph.hash("password2"))
    c1 = Client(name="client_u1_1", user=u1, token="aaaaAAAAbbbbBBBB0000111-C1")
    c2 = Client(name="client_u1_2", user=u1, token="aaaaAAAAbbbbBBBB0000111-C2")
    a1 = Application(
        name="app_c1_1", client=c1, routing_token="aaaaAAAAbbbbBBBB0000111-A1"
    )
    a2 = Application(
        name="app_c1_2", client=c1, routing_token="aaaaAAAAbbbbBBBB0000111-A2"
    )
    m1 = Message(body="Body1", priority="NORMAL", subject="Subject1", target=a1)
    m2 = Message(body="Body2", priority="NORMAL", subject="Subject2", target=a1)

    db.session.add_all([u1, u2, c1, c2, a1, a2, m1, m2])
    db.session.commit()
