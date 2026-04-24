from app.main import app
from tests.auth_helpers import create_admin_headers


def test_anonymous_request_is_audit_logged() -> None:
    client = app.test_client()

    health_resp = client.get("/health")
    assert health_resp.status_code == 200

    admin_headers = create_admin_headers(client)
    logs_resp = client.get("/api/v1/audit-logs?path=/health&method=GET", headers=admin_headers)

    assert logs_resp.status_code == 200
    body = logs_resp.json
    assert body["count"] >= 1
    assert any(log["path"] == "/health" for log in body["logs"])
    assert any(log["actor_type"] == "anonymous" for log in body["logs"])


def test_audit_logs_endpoint_is_admin_only() -> None:
    client = app.test_client()

    unauthorized_resp = client.get("/api/v1/audit-logs")
    assert unauthorized_resp.status_code == 401
