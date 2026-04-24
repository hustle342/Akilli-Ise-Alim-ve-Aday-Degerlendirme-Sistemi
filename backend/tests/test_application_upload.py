from io import BytesIO

from app.core.db import SessionLocal
from app.main import app
from app.models.entities import Invitation, MatchScore
from tests.auth_helpers import create_candidate_with_headers, create_hr_headers


def test_application_upload_flow() -> None:
    client = app.test_client()
    hr_headers = create_hr_headers(client)
    candidate_id, _, candidate_headers, _, _ = create_candidate_with_headers(client, "Test Candidate")

    job_resp = client.post(
        "/api/v1/jobs",
        json={
            "title": "Backend Developer",
            "description": "Python ve Flask gelistirme",
            "min_years_experience": 2,
            "required_skills": ["python", "flask", "sql"],
        },
        headers=hr_headers,
    )
    assert job_resp.status_code == 201
    job_posting_id = job_resp.json["id"]

    fake_pdf_content = (
        b"%PDF-1.4\n"
        b"Candidate has 4 years experience in Python Flask SQL Docker\n"
        b"%%EOF\n"
    )

    upload_resp = client.post(
        "/api/v1/applications/upload",
        data={
            "candidate_id": str(candidate_id),
            "job_posting_id": str(job_posting_id),
            "cv_file": (BytesIO(fake_pdf_content), "cv.pdf"),
        },
        content_type="multipart/form-data",
        headers=candidate_headers,
    )

    assert upload_resp.status_code == 201
    body = upload_resp.json
    assert body["candidate_id"] == candidate_id
    assert body["job_posting_id"] == job_posting_id
    assert "application_id" in body
    assert "parsed_summary" in body
    assert isinstance(body["extracted_skills"], list)
    assert "python" in body["extracted_skills"]
    assert body["estimated_years_experience"] >= 4
    assert body["match_score"] >= 70
    assert isinstance(body["score_reasons"], list)
    assert body["invitation_created"] is True

    session = SessionLocal()
    try:
        score_row = (
            session.query(MatchScore)
            .filter(MatchScore.application_id == body["application_id"])
            .first()
        )
        invitation_row = (
            session.query(Invitation)
            .filter(Invitation.application_id == body["application_id"])
            .first()
        )

        assert score_row is not None
        assert float(score_row.score) >= 70
        assert invitation_row is not None
    finally:
        session.close()
