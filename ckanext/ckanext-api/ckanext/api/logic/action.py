# encoding: utf-8
import ckan.plugins.toolkit as tk
import ckanext.api.logic.schema as schema
from ckan.types import Context, DataDict, Any
from ckan.common import _, config
import ckan.logic as logic
import ckan.lib.authenticator as authenticator
import ckan.lib.api_token as api_token
from  ckanext.api.model import ApiToken as api_token_model
from typing import Any, cast
import ckan.model as model
from ckan.views import user
from ckan.common import (
    _, config, current_user, login_user,
)
import logging
log = logging.getLogger(__name__)
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
    
    identity = {
            u"login": data.get("username"),
            u"password": data.get("password")
        }
    try: 
        user_obj = authenticator.ckan_authenticator(identity)
        if user_obj:
            #Thuc hien luu thong tin login 
            login_user(user_obj)
            # user.rotate_token()
            #TODO: Check state of user.
            # GET api token 
            # generate api token
            # user_obj.
            alias_api_token = user_obj.name + config.get('api_token.name_genergate', u'_API_TOKEN_DEFAULT')
            api_token_info = api_token_model.get_by_name(name=alias_api_token, user_id= user_obj.id)
            if api_token_info:
                _data = {
                    u'jti': api_token_info.id,
                    u'iat': api_token.into_seconds(api_token_info.created_at)
                }
                token = api_token.encode(_data)
                result = api_token.add_extra({u'token': token})
            else: 
                data_dict : dict[str, Any] = {
                u'name': alias_api_token,
                u'user': user_obj.id,
                }
                context = cast(Context, {
                    u'model': model,
                    u'session': model.Session,
                    u'user': current_user.name,
                    u'auth_user_obj': current_user
                })
                result =  logic.get_action('api_token_create')(context, data_dict)
        else:
            err = _(u"Login failed. Bad username or password.")
            raise logic.UsernamePasswordError(err)
    except Exception as e :
        log.error("Action login error")
        print(e)
        raise 
    return result
    

def get_actions():
    return {
        'login': login
    }
