import ckan.plugins.toolkit as tk


def new_template_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value


def get_validators():
    return {
        "new_template_required": new_template_required,
    }
