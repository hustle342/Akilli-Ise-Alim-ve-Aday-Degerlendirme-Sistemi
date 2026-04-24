from io import BytesIO

from app.main import app
from tests.auth_helpers import create_candidate_with_headers, create_hr_headers


def test_protected_job_endpoint_requires_token() -> None:
    client = app.test_client()

    resp = client.post(
        "/api/v1/jobs",
        json={
            "title": "Unauthorized Job",
            "description": "No token",
            "min_years_experience": 1,
            "required_skills": ["python"],
        },
    )

    assert resp.status_code == 401


def test_candidate_cannot_upload_for_another_candidate() -> None:
    client = app.test_client()
    hr_headers = create_hr_headers(client)

    candidate_one_id, _, candidate_one_headers, _, _ = create_candidate_with_headers(
        client, "Candidate One"
    )
    candidate_two_id, _, _, _, _ = create_candidate_with_headers(client, "Candidate Two")

    job_resp = client.post(
        "/api/v1/jobs",
        json={
            "title": "Secure Backend Job",
            "description": "Role restricted",
            "min_years_experience": 1,
            "required_skills": ["python", "flask"],
        },
        headers=hr_headers,
    )
    assert job_resp.status_code == 201
    job_id = job_resp.json["id"]

    fake_pdf_content = b"%PDF-1.4\nPython Flask 2 year experience\n%%EOF\n"

    upload_resp = client.post(
        "/api/v1/applications/upload",
        data={
            "candidate_id": str(candidate_two_id),
            "job_posting_id": str(job_id),
            "cv_file": (BytesIO(fake_pdf_content), "cv.pdf"),
        },
        content_type="multipart/form-data",
        headers=candidate_one_headers,
    )

    assert upload_resp.status_code == 403
    assert candidate_one_id != candidate_two_id
