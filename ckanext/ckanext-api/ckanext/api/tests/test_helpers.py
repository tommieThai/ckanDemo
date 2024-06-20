"""Tests for helpers.py."""

import ckanext.api.helpers as helpers


def test_api_hello():
    assert helpers.api_hello() == "Hello, api!"
