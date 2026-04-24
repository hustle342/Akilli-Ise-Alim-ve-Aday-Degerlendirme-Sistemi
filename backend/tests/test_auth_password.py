from app.main import app
from tests.auth_helpers import create_candidate_with_headers


def test_password_login_returns_access_and_refresh_tokens() -> None:
    client = app.test_client()
    _, email, _, password, _ = create_candidate_with_headers(client, "Password Candidate")

    login_resp = client.post(
        "/api/v1/auth/token",
        json={"email": email, "password": password},
    )

    assert login_resp.status_code == 200
    body = login_resp.json
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_refresh_token_issues_new_access_token() -> None:
    client = app.test_client()
    _, _, _, _, refresh_token = create_candidate_with_headers(client, "Refresh Candidate")

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json


def test_login_rejects_wrong_password() -> None:
    client = app.test_client()
    _, email, _, _, _ = create_candidate_with_headers(client, "Wrong Password Candidate")

    login_resp = client.post(
        "/api/v1/auth/token",
        json={"email": email, "password": "DefinitelyWrong1!"},
    )

    assert login_resp.status_code == 401
