"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.minio.logic import validators


def test_minio_reauired_with_valid_value():
    assert validators.minio_required("value") == "value"


def test_minio_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.minio_required(None)
