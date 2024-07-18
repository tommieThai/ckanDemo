from flask import Blueprint


minio = Blueprint(
    "minio", __name__)


def page():
    return "Hello, minio!"


minio.add_url_rule(
    "/minio/page", view_func=page)


def get_blueprints():
    return [minio]
