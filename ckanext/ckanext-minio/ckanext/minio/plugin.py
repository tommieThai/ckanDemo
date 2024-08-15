import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig
from ckan.views.resource import download as ckan_download
from ckanext.minio.logic.minio_con import MinioConnection
import ckanext.minio.logic.action.delete as delete
import ckanext.minio.logic.action.update as update
import ckanext.minio.logic.action.create as create
from ckanext.minio.logic.action.create import FileExtensionCheck,  get_prepare_resource_upload
import ckanext.minio.logic.validators as valid
from ckan.common import config
from ckan.lib.uploader import ResourceUpload
import os
import ckan.logic as logic
import ckan.logic
from typing import IO
import ckanext.minio.views as views

MB = 1 << 20

ValidationError = ckan.logic.ValidationError

minio_connection = None

#Kết nối Minio
def init_minio():
     global minio_connection
     if minio_connection is None:
         minio_connection = MinioConnection()

class MinioPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IUploader, inherit= True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IResourceController)

    # IConfigurer

    def update_config(self, config: CKANConfig):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("assets", "minio")
        init_minio()
     
    # IBlueprint

    def get_blueprint(self):
        # if minio_connection.is_connected():
        return views.get_blueprints()
       

    # IUploader

    #Tải dữ liệu lên Minio
    def get_resource_uploader(self, data_dict):
        # init_minio()
        if minio_connection.is_connected():
            return create.MinioResource(data_dict, minio_connection.get_client(), minio_connection.get_bucket_name())
        else:
            return ResourceUpload(data_dict)
        
    # IActions

    def get_actions(self):
        return {
            'resource_delete': delete.resource_minio_delete,
            'resource_update': update.resource_minio_update,
            'dataset_purge': delete.dataset_minio_purge
        }
    
     

    #IResourceController

    #helper func
    # def _validate_resource(self, resource):
    #     upload = get_prepare_resource_upload(resource)
    #     if upload :
    #         upload.verify_ext()
        # validator = FileExtensionCheck()
        # try:
        #     validator.check_ext(resource)
        # except ValidationError as e:
        #     raise toolkit.ValidationError(e.error_dict)

    def before_resource_create(self, context, resource):
        upload = get_prepare_resource_upload(resource)
        if upload :
            upload.verify_ext()

    def after_resource_create(self, context, resource):
        pass

    def before_resource_show(self, resource_dict):
        pass

    def before_resource_update(self, context, resource):
        upload = get_prepare_resource_upload(resource)
        if upload :
            upload.verify_ext()

    def after_resource_update(self, context, resource):
        pass  # You can implement post-update logic here if needed

    def before_resource_delete(self, context, resource, resources):
        pass  # Logic before resource deletion if needed

    def after_resource_delete(self, context, resources):
        pass  # Logic after resource deletion if needed




    

