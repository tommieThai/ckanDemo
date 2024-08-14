import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def api_login(context, data_dict):
    return {"success": True}


def get_auth_functions():
    return {
        "api_login": api_login
    }
