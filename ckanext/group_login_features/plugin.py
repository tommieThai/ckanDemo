from __future__ import annotations

from typing import Optional, cast
from ckan.types import (
AuthResult, Context, AuthFunction, ContextValidator, DataDict)
import ckan.plugins as plugins

import ckan.plugins.toolkit as toolkit


# import ckanext.phucthai.cli as cli
# import ckanext.phucthai.helpers as helpers
# import ckanext.phucthai.views as views
# from ckanext.phucthai.logic import (
#     action, auth, validators
# )

def group_create(
        context: Context,
        data_dict: Optional[DataDict] = None) -> AuthResult:
    # Get the user name of the logged-in user
    user_name: str= context['user']

    #Get a list of the members of the 'curators' group.
    try:
        members = toolkit.get_action('member_list')(
            {},
            {'id': 'curators', 'object_type': 'user'})
    except toolkit.ObjectNotFound:
        # The curators group doesn't exist.
        return {'success': False,
                'msg': "The curators groups doesn't exist, so only sysadmins "
                       "are authorized to create groups."}
    #'members' is a list of (user_id, object_type, capacity) tuples, we're 
    #only interested in the user_ids.
    member_ids = [member_typle[0] for member_tuple in members]

    #We have the logged-in user's user name, get their user_id.
    convert_user_name_or_id_to_id = cast(
            ContextValidator,
            toolkit.get_converter('convert_user_name_or_id_to_id'))
    try:
        user_id = convert_user_name_or_id_to_id(user_name, context)
    except toolkit.Invalid:
        #The user doesn't exist (e.g. they're not logged-in).
        return {'success': False,
                'msg':'You must be logged-in as a member of the curators'
                      'group to create new groups.'}
    #Finally, we can test whether the user is a member of the curators group.

    if user_id in member_ids:
        return {'success': True}
    else:
        return {'success': False,
                'msg': "Only curators are allowed to create groups"}

class PhucthaiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthFunctions)

    # plugins.implements(plugins.IAuthFunctions)
    # plugins.implements(plugins.IActions)
    # plugins.implements(plugins.IBlueprint)
    # plugins.implements(plugins.IClick)
    # plugins.implements(plugins.ITemplateHelpers)
    # plugins.implements(plugins.IValidators)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "phucthai")


    # IAuthFunctions

    def get_auth_functions(self) -> dict[str,AuthFunction]:
        return {'group_create': group_create}

    # IActions

    # def get_actions(self):
    #     return action.get_actions()

    # IBlueprint

    # def get_blueprint(self):
    #     return views.get_blueprints()

    # IClick

    # def get_commands(self):
    #     return cli.get_commands()

    # ITemplateHelpers

    # def get_helpers(self):
    #     return helpers.get_helpers()

    # IValidators

    # def get_validators(self):
    #     return validators.get_validators()