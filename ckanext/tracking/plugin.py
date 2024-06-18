# import click
# import ckan.plugins as p

# from typing import Any, Callable

# from ckan.plugins import toolkit
# from ckan.types import Context, CKANApp
# from ckan.common import CKANConfig

# from .cli.tracking import tracking
# from .helpers import popular
# from .middleware import track_request
# from .model import TrackingSummary


# class TrackingPlugin(p.SingletonPlugin):
#     p.implements(p.IClick)
#     p.implements(p.IConfigurer)
#     p.implements(p.IMiddleware, inherit=True)
#     p.implements(p.IPackageController, inherit=True)
#     p.implements(p.ITemplateHelpers)

#     # IClick
#     def get_commands(self) -> "list[click.Command]":
#         return [tracking]

#     # IConfigurer
#     def update_config(self, config: CKANConfig) -> None:
#         toolkit.add_resource("assets", "tracking")
#         toolkit.add_template_directory(config, "templates")

#     # IMiddleware
#     def make_middleware(self, app: CKANApp, config: CKANConfig) -> Any:
#         app.after_request(track_request)
#         return app

#     # IPackageController
#     def after_dataset_show(
#             self,
#             context: Context,
#             pkg_dict: "dict[str, Any]"
#             ) -> "dict[str, Any]":
#         """Appends tracking summary data to the package dict.

#         Tracking data is not stored in Solr so we need to retrieve it
#         from the database.
#         """
#         tracking_summary = TrackingSummary.get_for_package(
#             pkg_dict["id"]
#             )
#         pkg_dict["tracking_summary"] = tracking_summary

#         for resource_dict in pkg_dict['resources']:
#             summary = TrackingSummary.get_for_resource(
#                 resource_dict['url']
#                 )
#             resource_dict['tracking_summary'] = summary

#         return pkg_dict

#     def after_dataset_search(
#             self,
#             search_results: "dict[str, Any]",
#             search_params: "dict[str, Any]"
#             ) -> "dict[str, Any]":
#         """Add tracking summary to search results.

#         Tracking data is indexed but not stored in Solr so we need to
#         fetch it from the database. This can cause some discrepancies since
#         the number of views when indexing might have been different than
#         when this code is run.
#         """
#         for package_dict in search_results["results"]:
#             tracking_summary = TrackingSummary.get_for_package(
#                 package_dict["id"]
#                 )
#             package_dict["tracking_summary"] = tracking_summary
#             for resource_dict in package_dict['resources']:
#                 summary = TrackingSummary.get_for_resource(
#                     resource_dict['url']
#                     )
#                 resource_dict['tracking_summary'] = summary
#         return search_results

#     def before_dataset_index(
#             self, pkg_dict: "dict[str, Any]"
#             ) -> "dict[str, Any]":
#         """ Index tracking information.

#         This method will index (but not store) the tracking information of
#         the dataset. This will only allow us to sort Solr's queries by views.
#         For the actual data we will query the database after the search.

#         It will also remove the tracking_summary key from the package dict
#         since it is not a valid Solr field.
#         """
#         pkg_dict.pop("tracking_summary", None)
#         for r in pkg_dict.get('resources', []):
#             r.pop('tracking_summary', None)

#         tracking_summary = TrackingSummary.get_for_package(
#             pkg_dict["id"]
#             )
#         pkg_dict['views_total'] = tracking_summary['total']
#         pkg_dict['views_recent'] = tracking_summary['recent']
#         return pkg_dict

#     # ITemplateHelpers
#     def get_helpers(self) -> "dict[str, Callable[...,Any]]":
#         return {
#             "popular": popular,
#         }

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

