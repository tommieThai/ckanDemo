import ckan.plugins.toolkit as tk
from ckan.logic import ValidationError
from ckan.types import Context
import os


def minio_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value


def get_validators():
    return {
        "minio_required": minio_required,
    }


ALLOWED_EXTENSIONS = {'.txt', '.csv', '.png'}

def validate_file_extension(resource, context):
    upload_field = resource.get('name', None)
    print (upload_field)
    
    if not upload_field:
        raise ValidationError({'upload': ['No file uploaded or invalid file data']})
    
    _, ext = os.path.splitext(upload_field)
    
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise ValidationError({'upload': [f'File extension {ext} is not allowed. Allowed extensions are: {", ".join(ALLOWED_EXTENSIONS)}']})

    return resource
