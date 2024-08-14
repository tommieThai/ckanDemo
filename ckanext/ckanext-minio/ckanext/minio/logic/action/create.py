import os
from typing import IO, Optional, Any

from werkzeug.utils import secure_filename

from ckan.lib.uploader import ResourceUpload
import ckan.logic as logic
import ckan.logic
import ckan.plugins as plugins
from ckan.common import config
from ckanext.minio.logic.minio_con import MinioConnection
import ckanext.minio.logic.validators as valid
from ckan.plugins import toolkit
from ckan.types import ErrorDict

import magic
import cgi
from werkzeug.datastructures import FileStorage as FlaskFileStorage

ALLOWED_UPLOAD_TYPES = (cgi.FieldStorage, FlaskFileStorage)


MB = 1 << 20

ValidationError = ckan.logic.ValidationError


#Kiểm tra dung lượng file đẩy lên
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

def get_prepare_resource_upload(data_dict: dict[str, Any]):
    '''Query IUploader plugins and return a resource uploader instance.'''
    upload = None

    # default uploader
    if upload is None:
        upload = FileExtensionCheck(data_dict)

    return upload

class FileExtensionCheck(object):
    allowed_extensions = toolkit.aslist(config.get("ckanext_minio.allowed_extensions", "txt pdf csv png jpeg"))
    filename: Optional[str]
    upload_file: Optional[IO[bytes]]
    url: Optional[str]
    url_type: Optional[str]

    def __init__(self, resource: dict[str, Any],
                 filename: Optional[str] = None,
                 ) -> None:
        data = resource.get('upload', None)
        if filename is None:
            # url = resource.get('url')
            if data is not None:
                file_name  = secure_filename(resource.get('upload').filename)
            else: file_name = ''
            self.filename = file_name
        else: 
            self.filename = filename
        self.url =  resource.get('url')
        self.upload_file = resource.get('upload', None)
        if bool(self.upload_file) and \
                isinstance(self.upload_file, ALLOWED_UPLOAD_TYPES):
            self.url_type = 'upload'
        else:
            self.url_type = ''

    def _check_ext(self,ext_file: str):
        if not self.allowed_extensions: return
        
        if self.allowed_extensions and  ext_file not in self.allowed_extensions:
            err: ErrorDict = {
            'upload': [toolkit._(f"Unsupported upload file!")]
            }
            raise logic.ValidationError(err)
        
    def verify_ext(self):
        if self.url_type != 'upload':
            if self.url != '' and self.url is not None:
                self._check_ext(self.url.lower().split('.')[-1])
        else: 
            if not self.filename or not self.upload_file:
                return

            mimetypes = plugins.toolkit.aslist(config.get(
                f"ckan.upload.resource.mimetypes",[]))
            types = plugins.toolkit.aslist(config.get(f"ckan.upload.resource.types", []))
            # ext_files = plugins.toolkit.aslist(config.get(f"ckan.upload.resource.files"))
            if not mimetypes and not types:
                return
            
            ext_file = self.filename.lower().split('.')[-1]
            self._check_ext(ext_file)
            
            file = self.upload_file
            file_content = file.read()
            actual = magic.from_buffer(file_content, mime=True)
            file.seek(0, os.SEEK_SET)
            err: ErrorDict = {
                        'upload': [plugins.toolkit._(f"Unsupported upload type: ") + actual]
                }
            if mimetypes and actual not in mimetypes:
                    raise logic.ValidationError(err)

            type_ = actual.split("/")[0]

            if types and type_ not in types:
                    raise logic.ValidationError(err)


    # def check_resource(self, resource):
    #     if not resource or not resource.get('name'):
    #         raise ValidationError({'upload': ['No file uploaded or invalid file data']})
        
    # def get_ext(self, filename: str) -> str:
    #     return filename.rsplit('.', 1)[-1].lower()
    
    # def check_ext(self, resource):
    #     if not self.check_resource(resource):
    #         return

    #     filename = resource.get('name')
    #     ext = self.get_ext(filename)
    #     print ("extension: ", ext)

    #     if f".{ext}" not in self.allowed_extensions:
    #         raise ValidationError({'upload': [f'File extension {ext} is not allowed.']})


        
class MinioResource(ResourceUpload):

    def __init__(self, resource, client, bucket_name):
        super(MinioResource, self).__init__(resource)
        self.client = client
        self.bucket_name = bucket_name
        self.resource = resource
        self.package_id = resource.get("package_id", None)
        # self.validator = FileExtensionCheck()

    
    def get_path_minio(self, pkg: str,id: str) -> str:
        object_name = f'{pkg}/{id}'
        filepath = self.client.presigned_get_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
        )        

        if filepath is None or filepath == "":
            raise logic.ValidationError({'upload': ['Invalid storage path']})
        return filepath    

    def upload(self, id: str, max_size: int = 10) -> None:
        # self.validator.check_ext(self.resource)

        if not self.storage_path:
            return
        
        if self.package_id is None or self.package_id == "":
            return 

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
            if self.client:
                if self.mimetype is None or self.mimetype == "":
                    self.mimetype = "application/octet-stream"
                self.client.fput_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name, 
                    file_path=tmp_filepath, 
                    content_type=self.mimetype
                )
                
            os.remove(tmp_filepath)
            return 'file uploaded'
        
        # The resource form only sets self.clear (via the input clear_upload)
        # to True when an uploaded file is not replaced by another uploaded
        # file, only if it is replaced by a link to file.
        # If the uploaded file is replaced by a link, we should remove the
        # previously uploaded file to clean up the file system.
        if self.clear and self.client:
            try:
                self.client.remove_object(self.bucket_name, object_name)
            except OSError:
                pass