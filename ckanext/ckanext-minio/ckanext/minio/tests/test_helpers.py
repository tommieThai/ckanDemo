"""Tests for helpers.py."""

import ckanext.minio.helpers as helpers


def test_minio_hello():
    assert helpers.minio_hello() == "Hello, minio!"
