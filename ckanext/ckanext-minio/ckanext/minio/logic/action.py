import ckan.plugins.toolkit as tk
import ckanext.minio.logic.schema as schema


@tk.side_effect_free
def minio_get_sum(context, data_dict):
    tk.check_access(
        "minio_get_sum", context, data_dict)
    data, errors = tk.navl_validate(
        data_dict, schema.minio_get_sum(), context)

    if errors:
        raise tk.ValidationError(errors)

    return {
        "left": data["left"],
        "right": data["right"],
        "sum": data["left"] + data["right"]
    }


def get_actions():
    return {
        'minio_get_sum': minio_get_sum,
    }
