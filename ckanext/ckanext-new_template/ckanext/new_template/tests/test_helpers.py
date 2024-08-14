"""Tests for helpers.py."""

import ckanext.new_template.helpers as helpers


def test_new_template_hello():
    assert helpers.new_template_hello() == "Hello, new_template!"
