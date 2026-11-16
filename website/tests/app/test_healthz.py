import pytest


@pytest.mark.django_db
def test_healthz_returns_ok_without_db_queries(client, django_assert_num_queries):
    with django_assert_num_queries(0):
        response = client.get("/healthz/")

    assert response.status_code == 200
    assert response.content == b"ok"
    assert response["Content-Type"].startswith("text/plain")
