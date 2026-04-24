from io import BytesIO

from app.main import app
from tests.auth_helpers import create_candidate_with_headers, create_hr_headers


def _create_job(client, headers) -> int:
    resp = client.post(
        "/api/v1/jobs",
        json={
            "title": "Backend Developer",
            "description": "API ve veri tabani gelistirme",
            "min_years_experience": 2,
            "required_skills": ["python", "flask", "sql"],
        },
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json["id"]


def _upload_cv(client, candidate_id: int, job_posting_id: int, content: bytes, headers):
    resp = client.post(
        "/api/v1/applications/upload",
        data={
            "candidate_id": str(candidate_id),
            "job_posting_id": str(job_posting_id),
            "cv_file": (BytesIO(content), "cv.pdf"),
        },
        content_type="multipart/form-data",
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json


def test_job_candidate_listing_and_shortlist() -> None:
    client = app.test_client()
    hr_headers = create_hr_headers(client)
    job_id = _create_job(client, hr_headers)

    high_id, _, high_headers, _, _ = create_candidate_with_headers(client, "High Candidate")
    low_id, _, low_headers, _, _ = create_candidate_with_headers(client, "Low Candidate")

    high_cv = (
        b"%PDF-1.4\n"
        b"Python Flask SQL Docker 4 year experience\n"
        b"%%EOF\n"
    )
    low_cv = (
        b"%PDF-1.4\n"
        b"No matching stack 0 year experience\n"
        b"%%EOF\n"
    )

    high_upload = _upload_cv(client, high_id, job_id, high_cv, high_headers)
    low_upload = _upload_cv(client, low_id, job_id, low_cv, low_headers)

    assert high_upload["match_score"] > low_upload["match_score"]

    listing_resp = client.get(f"/api/v1/jobs/{job_id}/candidates", headers=hr_headers)
    assert listing_resp.status_code == 200
    listing_body = listing_resp.json

    assert listing_body["candidate_count"] >= 2
    candidates = listing_body["candidates"]
    assert candidates[0]["match_score"] >= candidates[1]["match_score"]

    shortlist_resp = client.get(
        f"/api/v1/jobs/{job_id}/shortlisted?threshold=70", headers=hr_headers
    )
    assert shortlist_resp.status_code == 200
    shortlist_body = shortlist_resp.json

    assert shortlist_body["shortlisted_count"] >= 1
    assert all(item["score"] >= 70 for item in shortlist_body["candidates"])


def test_invitation_tracking_endpoint() -> None:
    client = app.test_client()
    hr_headers = create_hr_headers(client)
    job_id = _create_job(client, hr_headers)

    candidate_id, _, candidate_headers, _, _ = create_candidate_with_headers(client, "Invited Candidate")

    high_cv = (
        b"%PDF-1.4\n"
        b"Python Flask SQL Docker 5 year experience\n"
        b"%%EOF\n"
    )
    upload_body = _upload_cv(client, candidate_id, job_id, high_cv, candidate_headers)
    assert upload_body["invitation_created"] is True

    invitations_resp = client.get(
        f"/api/v1/invitations?job_posting_id={job_id}", headers=hr_headers
    )
    assert invitations_resp.status_code == 200
    invitations_body = invitations_resp.json
    assert invitations_body["count"] >= 1

    sent_resp = client.get("/api/v1/invitations?status=sent", headers=hr_headers)
    assert sent_resp.status_code == 200
    sent_body = sent_resp.json
    assert sent_body["count"] >= 1

    bad_status_resp = client.get("/api/v1/invitations?status=unknown", headers=hr_headers)
    assert bad_status_resp.status_code == 400
