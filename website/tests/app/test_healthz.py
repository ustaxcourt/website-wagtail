import pytest


@pytest.mark.django_db
class TestHealthz:
    def test_returns_ok(self, client):
        response = client.get("/healthz/")
        assert response.status_code == 200
        assert response.content == b"ok"
        assert response["Content-Type"].startswith("text/plain")

    def test_makes_no_database_queries(self, client, django_assert_num_queries):
        """ECS/ALB health checks must not depend on the DB or page rendering."""
        with django_assert_num_queries(0):
            client.get("/healthz/")
