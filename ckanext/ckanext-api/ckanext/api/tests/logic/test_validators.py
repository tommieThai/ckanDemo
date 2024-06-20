"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.api.logic import validators


def test_api_reauired_with_valid_value():
    assert validators.api_required("value") == "value"


def test_api_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.api_required(None)
