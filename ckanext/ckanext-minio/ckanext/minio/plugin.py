import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig
from minio import Minio
from ckan.common import config
from ckan.plugins.interfaces import IUploader

# import ckanext.minio.cli as cli
# import ckanext.minio.helpers as helpers
# import ckanext.minio.views as views
# from ckanext.minio.logic import (
#     action, auth, validators
# )

def minio_connection():
    client = Minio(config.get("ckanext_minio.host_name", "127.0.0.1:9000"),
        access_key=config.get("ckanext_minio.access_key", "nerL1Zn3uuKtJ4f8nl6A"),
        secret_key=config.get("ckanext_minio.secret_access_key", "lDleMYsM8Wo5BT1ay9I5XAE2kDDrfiG0tVFwD3oa"),
        secure=False
    )

    if client.bucket_exists(toolkit.config.get("ckanext_minio.bucket_name", "ckan")):
        print("bucket exists")
    else:
        print("bucket does not exist!")
        client.make_bucket(toolkit.config.get("ckanext_minio.bucket_name", "ckan"))
        print("Đã tạo!")

def get_uploader():


    None

def get_resource_uploader():

    
    None

class MinioPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    
    # plugins.implements(plugins.IAuthFunctions)
    # plugins.implements(plugins.IActions)
    # plugins.implements(plugins.IBlueprint)
    # plugins.implements(plugins.IClick)
    # plugins.implements(plugins.ITemplateHelpers)
    # plugins.implements(plugins.IValidators)
    

    # IConfigurer

    def update_config(self, config: CKANConfig):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("assets", "minio")

    def configure(self, config):
        minio_connection()
    
    # IAuthFunctionsc

    # def get_auth_functions(self):
    #     return auth.get_auth_functions()

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
    #     '''Connect Database Minio to CKAN'''
    #     return {'check_minio_connection': minio_connection}

    # IValidators

    # def get_validators(self):
    #     return validators.get_validators()
    
