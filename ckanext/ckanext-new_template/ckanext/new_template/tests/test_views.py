"""Tests for views.py."""

import pytest

import ckanext.new_template.validators as validators


import ckan.plugins.toolkit as tk


@pytest.mark.ckan_config("ckan.plugins", "new_template")
@pytest.mark.usefixtures("with_plugins")
def test_new_template_blueprint(app, reset_db):
    resp = app.get(tk.h.url_for("new_template.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, new_template!"
