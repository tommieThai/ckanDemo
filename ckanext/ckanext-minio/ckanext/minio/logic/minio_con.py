from minio import Minio
from ckan.common import config
from ckan.plugins.toolkit import asbool

class MinioConnection:
    client = None
    bucket_name = None
    minio_enabled = None
    def __init__(self):
        # self.client = None
        self.bucket_name = config.get("ckanext_minio.bucket_name", "ckan")
        self.minio_enabled = asbool(config.get("minio_enabled", False))
        if self.minio_enabled:
            self.init_minio_client()

    def init_minio_client(self):
        self.client = Minio(
            config.get("ckanext_minio.host_name", "127.0.0.1:9000"),
            access_key=config.get("ckanext_minio.access_key", "nerL1Zn3uuKtJ4f8nl6A"),
            secret_key=config.get("ckanext_minio.secret_access_key", "lDleMYsM8Wo5BT1ay9I5XAE2kDDrfiG0tVFwD3oa"),
            secure=False
        )
        print ("init_minio_client: ", self.client)
        self.ensure_bucket_exists()

    def ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def get_client(self):
        return self.client

    def is_enabled(self):
        return self.minio_enabled

    def get_bucket_name(self):
        return self.bucket_name
