# encoding: utf-8
from __future__ import annotations
from minio import Minio
from ckan.common import config
from ckan.plugins.toolkit import asbool
import logging
from minio.error import S3Error
log = logging.getLogger(__name__)

class MinioConnection:
    max_count = 3
    client = None
    bucket_name = None
    minio_connected = False
    def __init__(self):
        # self.client = None
        self.bucket_name = config.get("ckanext_minio.bucket_name", "ckan")
        minio_enabled = asbool(config.get("minio_enabled", False))

        if minio_enabled and not self.is_connected :
            self.init_minio_client()

    def init_minio_client(self):
        try: 
            self.client = Minio(
                config.get("ckanext_minio.host_name", "127.0.0.1:9000"),
                access_key=config.get("ckanext_minio.access_key", "nerL1Zn3uuKtJ4f8nl6A"),
                secret_key=config.get("ckanext_minio.secret_access_key", "lDleMYsM8Wo5BT1ay9I5XAE2kDDrfiG0tVFwD3oa"),
                secure=False
            )
            print ("init_minio_client: ", self.client)
            self.ensure_bucket_exists()
            self.minio_connected = True
        except S3Error as exc:
            print("error occurred.", exc)
            log.error("Connect Minio failed: ", str(exc))
            if self.max_count > 0:
                self.max_count = self.max_count - 1
                self.init_minio_client()



    def ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def get_client(self):
        return self.client

    def is_connected(self):
        return self.minio_connected

    def get_bucket_name(self):
        return self.bucket_name
