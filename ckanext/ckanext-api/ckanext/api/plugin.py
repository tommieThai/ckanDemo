from __future__ import annotations
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

# import ckanext.api.cli as cli
# import ckanext.api.helpers as helpers
# import ckanext.api.views as views
from ckanext.api.logic import (
    action, auth, validators
)
from ckan.config.declaration import Declaration, Key

class ApiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)
    # plugins.implements(plugins.IBlueprint)
    # plugins.implements(plugins.IClick)
    # plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IConfigDeclaration)
    

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "api")
        
    def declare_config_options(self, declaration: Declaration, key: Key= None):
        self._load_declaration(declaration)
        
    def _load_declaration(self, declaration: Declaration):
        import os
        import yaml
        filename = os.path.join(
            os.path.dirname(__file__),
            "config_declaration.yaml"
        )
        with open(filename) as src:
            data = yaml.safe_load(src)

        try:
            declaration.load_dict(data)
        except ValueError:
            # we a loading two recline plugins that are share config declaration.
            pass
    # IAuthFunctions

    def get_auth_functions(self):
        return auth.get_auth_functions()

    # IActions

    def get_actions(self):
        return action.get_actions()

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

    def get_validators(self):
        return validators.get_validators()
    
