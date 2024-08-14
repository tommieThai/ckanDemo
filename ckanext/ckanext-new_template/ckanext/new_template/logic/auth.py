import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def new_template_get_sum(context, data_dict):
    return {"success": True}


def get_auth_functions():
    return {
        "new_template_get_sum": new_template_get_sum,
    }
