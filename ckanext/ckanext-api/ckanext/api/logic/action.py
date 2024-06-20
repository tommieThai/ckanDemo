# encoding: utf-8
import ckan.plugins.toolkit as tk
import ckanext.api.logic.schema as schema
from ckan.types import Context, DataDict
from ckan.common import _
import ckan.logic as logic
import ckan.lib.authenticator as authenticator

_check_access = logic.check_access

@tk.side_effect_free    
def login(context: Context, data_dict: DataDict):
    #TODO: Check access feature api login
    _check_access('api_login', context, data_dict)
    #TODO: Check params/body
    # if username_or_email is None or password is None:
    data, errors = tk.navl_validate(
        data_dict, schema.api_login(), context)
    if errors:
        raise tk.ValidationError(errors)
    print(data)
    identity = {
            u"login": data.get("username"),
            u"password": data.get("password")
        }
    user_obj = authenticator.ckan_authenticator(identity)
    if user_obj:
        #TODO: Check state of user.
        # GET api token 
        # generate api token
        print() 
    else:
        err = _(u"Login failed. Bad username or password.")
        #TODO: return error
    
    #Return API token
    return "OK"
    


def get_actions():
    return {
        'login': login
    }
