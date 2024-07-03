"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.new_template.logic import validators


def test_new_template_reauired_with_valid_value():
    assert validators.new_template_required("value") == "value"


def test_new_template_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.new_template_required(None)
