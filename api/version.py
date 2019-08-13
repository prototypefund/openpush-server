import app
from flask import jsonify


def search():
    return jsonify({"version": app.API_VERSION})
