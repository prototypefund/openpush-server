class Config:
    DEBUG = False
    TESTING = False
    APP_PORT = 5000
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USER = None
    PASS = None


class ProdConfig(Config):
    ENV = "production"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"


class DevConfig(Config):
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"
    # SQLALCHEMY_ECHO = True
    USER = "admin"
    PASS = "admin"


class TestConfig(Config):
    ENV = "test"
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
