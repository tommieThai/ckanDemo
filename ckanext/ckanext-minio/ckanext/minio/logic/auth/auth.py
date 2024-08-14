import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def minio_get_sum(context, data_dict):
    return {"success": True}


def get_auth_functions():
    return {
        "minio_get_sum": minio_get_sum,
    }
