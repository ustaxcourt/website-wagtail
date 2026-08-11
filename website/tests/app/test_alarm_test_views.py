"""Tests for app/alarm_test_views.py."""

import pytest
from django.test import override_settings


pytestmark = pytest.mark.django_db


@override_settings(ENABLE_ERROR_TEST_PAGES=False, GITHUB_SHA="test-sha")
def test_alarm_test_index_404_when_disabled(client):
    response = client.get("/alarm-test/")
    assert response.status_code == 404


@override_settings(ENABLE_ERROR_TEST_PAGES=True)
def test_alarm_test_index_lists_all_alarm_endpoints(client):
    response = client.get("/alarm-test/")
    body = response.content.decode("utf-8")

    assert response.status_code == 200
    assert "/alarm-test/trigger-5xx/" in body
    assert "/alarm-test/trigger-404/" in body
    assert "/alarm-test/trigger-rds-error/" in body


@override_settings(ENABLE_ERROR_TEST_PAGES=True, GITHUB_SHA="test-sha")
def test_trigger_404_returns_404(client):
    response = client.get("/alarm-test/trigger-404/")
    assert response.status_code == 404


@override_settings(ENABLE_ERROR_TEST_PAGES=True, DEBUG=False)
def test_trigger_5xx_returns_500(client):
    client.raise_request_exception = False
    response = client.get("/alarm-test/trigger-5xx/")
    assert response.status_code == 500


@override_settings(ENABLE_ERROR_TEST_PAGES=True, DEBUG=False)
def test_trigger_rds_error_returns_500(client):
    client.raise_request_exception = False
    response = client.get("/alarm-test/trigger-rds-error/")
    assert response.status_code == 500
