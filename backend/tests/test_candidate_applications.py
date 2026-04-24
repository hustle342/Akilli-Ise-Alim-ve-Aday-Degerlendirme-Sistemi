from io import BytesIO

from app.main import app
from tests.auth_helpers import create_candidate_with_headers, create_hr_headers


def test_candidate_can_list_own_applications() -> None:
    client = app.test_client()
    hr_headers = create_hr_headers(client)
    candidate_id, _, candidate_headers, _, _ = create_candidate_with_headers(
        client,
        "Candidate Applications",
    )

    job_resp = client.post(
        "/api/v1/jobs",
        json={
            "title": "Mobile Developer",
            "description": "Flutter ve API entegrasyonu",
            "min_years_experience": 1,
            "required_skills": ["flutter", "dart", "git"],
        },
        headers=hr_headers,
    )
    assert job_resp.status_code == 201
    job_id = job_resp.json["id"]

    upload_resp = client.post(
        "/api/v1/applications/upload",
        data={
            "candidate_id": str(candidate_id),
            "job_posting_id": str(job_id),
            "cv_file": (
                BytesIO(b"%PDF-1.4\nFlutter Dart Git 2 year experience\n%%EOF\n"),
                "cv.pdf",
            ),
        },
        content_type="multipart/form-data",
        headers=candidate_headers,
    )
    assert upload_resp.status_code == 201

    listing_resp = client.get("/api/v1/applications/me", headers=candidate_headers)
    assert listing_resp.status_code == 200

    body = listing_resp.json
    assert body["count"] >= 1
    first = body["applications"][0]
    assert first["job_posting_id"] == job_id
    assert first["job_title"] == "Mobile Developer"
    assert first["match_score"] is not None


def test_candidate_can_list_available_jobs() -> None:
    client = app.test_client()
    hr_headers = create_hr_headers(client)
    _, _, candidate_headers, _, _ = create_candidate_with_headers(
        client,
        "Candidate Job Browser",
    )

    job_resp = client.post(
        "/api/v1/jobs",
        json={
            "title": "QA Engineer",
            "description": "Test surecleri ve otomasyon",
            "min_years_experience": 1,
            "required_skills": ["python", "git"],
        },
        headers=hr_headers,
    )
    assert job_resp.status_code == 201

    listing_resp = client.get("/api/v1/jobs", headers=candidate_headers)
    assert listing_resp.status_code == 200
    body = listing_resp.json

    assert body["count"] >= 1
    assert any(job["title"] == "QA Engineer" for job in body["jobs"])
