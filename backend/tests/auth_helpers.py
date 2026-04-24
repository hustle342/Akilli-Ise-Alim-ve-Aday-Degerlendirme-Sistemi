from uuid import uuid4


def create_admin_headers(client):
    email = f"admin_{uuid4().hex[:8]}@example.com"
    password = "AdminPass123!"
    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Admin User",
            "email": email,
            "password": password,
            "role": "admin",
            "bootstrap_code": "dev-bootstrap-code",
        },
    )
    assert register_resp.status_code == 201

    token_resp = client.post(
        "/api/v1/auth/token", json={"email": email, "password": password}
    )
    assert token_resp.status_code == 200

    token = token_resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_hr_headers(client):
    email = f"hr_{uuid4().hex[:8]}@example.com"
    password = "HrPass123!"
    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "HR User",
            "email": email,
            "password": password,
            "role": "hr",
            "bootstrap_code": "dev-bootstrap-code",
        },
    )
    assert register_resp.status_code == 201

    token_resp = client.post(
        "/api/v1/auth/token", json={"email": email, "password": password}
    )
    assert token_resp.status_code == 200

    token = token_resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_candidate_with_headers(client, full_name: str):
    email = f"candidate_{uuid4().hex[:8]}@example.com"
    password = "Candidate123!"

    candidate_resp = client.post(
        "/api/v1/candidates",
        json={"full_name": full_name, "email": email, "password": password},
    )
    assert candidate_resp.status_code == 201

    token_resp = client.post(
        "/api/v1/auth/token", json={"email": email, "password": password}
    )
    assert token_resp.status_code == 200

    token = token_resp.json["access_token"]
    refresh_token = token_resp.json["refresh_token"]
    return (
        candidate_resp.json["id"],
        email,
        {"Authorization": f"Bearer {token}"},
        password,
        refresh_token,
    )
