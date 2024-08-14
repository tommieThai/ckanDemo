from flask import Blueprint


new_template = Blueprint(
    "new_template", __name__)


def page():
    return "Hello, new_template!"


new_template.add_url_rule(
    "/new_template/page", view_func=page)


def get_blueprints():
    return [new_template]
