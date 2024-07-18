import ckan.plugins.toolkit as tk


def minio_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value


def get_validators():
    return {
        "minio_required": minio_required,
    }
