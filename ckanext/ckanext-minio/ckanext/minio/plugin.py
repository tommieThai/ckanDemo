import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig
from minio import Minio
from ckan.common import config
from ckan.lib.uploader import ResourceUpload
import os
import ckan.logic as logic
import ckan.logic
from typing import IO
import ckan.model as model
import ckanext.minio.views as views


MB = 1 << 20

# import ckanext.minio.cli as cli
# import ckanext.minio.helpers as helpers
# import ckanext.minio.views as views
# from ckanext.minio.logic import (
#     action, auth, validators
# )

ValidationError = ckan.logic.ValidationError

ori_action_update = toolkit.get_action('resource_update')

def resource_minio_update(context, data_dict):
    resource_id = data_dict.get('id')
    new_file = data_dict.get('upload')

    resource = toolkit.get_action('resource_show')(context, {'id': resource_id})
    
    package_id = resource.get('package_id')
    package = toolkit.get_action('package_show')(context, {'id': package_id})
    package_name = package.get('name')

    if resource.get('url_type') == 'upload':
        client = Minio(
            toolkit.config.get("ckanext_minio.host_name", "127.0.0.1:9000"),
            access_key=toolkit.config.get("ckanext_minio.access_key", "nerL1Zn3uuKtJ4f8nl6A"),
            secret_key=toolkit.config.get("ckanext_minio.secret_access_key", "lDleMYsM8Wo5BT1ay9I5XAE2kDDrfiG0tVFwD3oa"),
            secure=False
        )
        
        bucket_name = toolkit.config.get("ckanext_minio.bucket_name", "ckan")
        object_name = f'{package_name}/{resource["id"]}'

        try:
            tmp_filepath = '/tmp/' + new_file.filename
            new_file.save(tmp_filepath)

            client.fput_object(
                bucket_name=bucket_name, 
                object_name=object_name, 
                file_path=tmp_filepath, 
                content_type=new_file.mimetype
            )

            os.remove(tmp_filepath)
        except Exception as e:
            errors = f'{"resource_update": ["Error updating resource in Minio: " + str(e)]}'
            raise ValidationError(errors)
        
    return ori_action_update(context, data_dict)

ori_action_delete = toolkit.get_action('resource_delete')

def resource_minio_delete(context, data_dict):
    resource_id = data_dict.get('id')

    resource = toolkit.get_action('resource_show')(context, {'id': resource_id})

    package_id = resource.get('package_id')
    package = toolkit.get_action('package_show')(context, {'id': package_id})
    package_name = package.get('name')

    if resource.get('url_type') == 'upload':
        client = Minio(
            toolkit.config.get("ckanext_minio.host_name", "127.0.0.1:9000"),
            access_key=toolkit.config.get("ckanext_minio.access_key", "nerL1Zn3uuKtJ4f8nl6A"),
            secret_key=toolkit.config.get("ckanext_minio.secret_access_key", "lDleMYsM8Wo5BT1ay9I5XAE2kDDrfiG0tVFwD3oa"),
            secure=False
        )

        bucket_name = toolkit.config.get("ckanext_minio.bucket_name", "ckan")
        object_name = f'{package_name}/{resource["id"]}'

        try:
            client.remove_object(bucket_name= bucket_name, object_name= object_name)
        except Exception as e:
            errors = f'{"resource_delete": ["Error deleting resource from Minio: " + str(e)]}'
            raise ValidationError(errors)
        
    return ori_action_delete(context, data_dict)

def minio_connection():
    if toolkit.asbool(config.get("minio_enabled", False)):
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

def _copy_file(input_file: IO[bytes],
            output_file: IO[bytes], max_size: int) -> None:
    input_file.seek(0)
    current_size = 0
    while True:
        current_size = current_size + 1
        # MB chunks
        data = input_file.read(MB)

        if not data:
            break
        output_file.write(data)
        if current_size > max_size:
            raise logic.ValidationError({'upload': ['File upload too large']})

# Class CreateView -> resource_create() -> get_resource_uploader() -> class ResoureUpload -> get_directory()

class MinioResource(ResourceUpload):
    client = None
    bucket_name = None
    package_id = None
    

    def __init__(self, resource):
        super(MinioResource, self).__init__(resource)
        self.minio_enabled = config.get("minio_enabled", False)
        if self.minio_enabled:
            self.client = Minio(config.get("ckanext_minio.host_name", "127.0.0.1:9000"),
            access_key=config.get("ckanext_minio.access_key", "nerL1Zn3uuKtJ4f8nl6A"),
            secret_key=config.get("ckanext_minio.secret_access_key", "lDleMYsM8Wo5BT1ay9I5XAE2kDDrfiG0tVFwD3oa"),
            secure=False
            )
        self.resource = resource
        self.bucket_name = toolkit.config.get("ckanext_minio.bucket_name", "ckan")

        self.package_id = resource.get("package_id", None)
        # print (self.package_id)
        # self.resource_id = self.resource.get("id", None)
    
    def get_path_minio(self, pkg: str,id: str) -> str:
        object_name = f'{pkg}/{id}'
        filepath = self.client.presigned_get_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
        )        
        # directory = self.get_directory(id)
        # filepath = os.path.join(directory, id[6:])

        if filepath is None or filepath == "":
            raise logic.ValidationError({'upload': ['Invalid storage path']})
        # print ("Test thu: ", filepath)
        return filepath    

    def upload(self, id: str, max_size: int = 10) -> None:
        if not self.storage_path:
            return
        
        if self.package_id is None or self.package_id == "":
            return 
        
        # package_exist = self.client.(package_id)
        # if not package_exist:
        #     self.resource
        


        object_name = f'{self.package_id}/{id}'

        filepath = self.get_path(id)
        directory = self.get_directory(id)

        if self.filename:
            # Create the directory if it doesn't exist
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno != 17:
                    raise
            tmp_filepath = filepath + '~' 
            with open(tmp_filepath, 'wb+') as output_file:
                assert self.upload_file
                try:
                    _copy_file(self.upload_file, output_file, max_size)
                except logic.ValidationError:
                    os.remove(tmp_filepath)
                    raise
                finally:
                    self.upload_file.close()
          

            # Upload the file to Minio
            if self.minio_enabled:
                if self.mimetype is None or self.mimetype == "":
                    self.mimetype = "application/octet-stream"
                self.client.fput_object(
                    bucket_name=self.bucket_name, object_name=object_name, file_path=tmp_filepath, content_type=self.mimetype
                )

                #Lấy URL trong Minio
                # minio_url = self.client.presigned_get_object(
                #     bucket_name=self.bucket_name,
                #     object_name=object_name,
                # )

                # # Update URL resource
                # context = {
                #     'model': model,
                #     'session': model.Session,
                # }

                # pkg_dict = logic.get_action('package_show')(context, {'id': package_id})
                # resource = pkg_dict['resources'][-1]
                # resource['url'] = minio_url
                # resource['url_type'] = 'upload'

                # logic.get_action('resource_create_default_resource_views')(context, 
                # {'resource': resource,
                #  'package': pkg_dict
                # })





            os.remove(tmp_filepath)
            return 'file uploaded'
        
        # The resource form only sets self.clear (via the input clear_upload)
        # to True when an uploaded file is not replaced by another uploaded
        # file, only if it is replaced by a link to file.
        # If the uploaded file is replaced by a link, we should remove the
        # previously uploaded file to clean up the file system.
        if self.clear and self.minio_enabled:
            try:
                self.client.remove_object(self.bucket_name, object_name)
            except OSError:
                pass
    

class MinioPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IUploader, inherit= True)
    
    # plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint)
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

    def get_resource_uploader(self, data_dict):
        if toolkit.asbool(config.get("minio_enabled", False)):
            return MinioResource(data_dict)
        else:
            return ResourceUpload(data_dict)

    # IAuthFunctionsc

    # def get_auth_functions(self):
    #     return auth.get_auth_functions()

    # IActions

    def get_actions(self):
        return {
            'resource_delete': resource_minio_delete,
            'resource_update': resource_minio_update
        }

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()

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
    
