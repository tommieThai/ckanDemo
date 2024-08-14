import ckan.plugins.toolkit as tk

def api_login_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value

def get_validators():
    return {
        "api_login_required": api_login_required
    }
