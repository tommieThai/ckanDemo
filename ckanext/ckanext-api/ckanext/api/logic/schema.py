import ckan.plugins.toolkit as tk


def api_login():
    not_empty = tk.get_validator("api_login_required")

    return {
        "username": [not_empty],
        "password": [not_empty]
    }
