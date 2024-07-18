"""Tests for views.py."""

import pytest

import ckanext.minio.validators as validators


import ckan.plugins.toolkit as tk


@pytest.mark.ckan_config("ckan.plugins", "minio")
@pytest.mark.usefixtures("with_plugins")
def test_minio_blueprint(app, reset_db):
    resp = app.get(tk.h.url_for("minio.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, minio!"
