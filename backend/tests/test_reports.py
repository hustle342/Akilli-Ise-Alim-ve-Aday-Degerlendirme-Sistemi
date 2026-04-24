from io import BytesIO

from app.main import app
from tests.auth_helpers import create_candidate_with_headers, create_hr_headers


def _create_job(client, headers) -> int:
    resp = client.post(
        "/api/v1/jobs",
        json={
            "title": "Data Engineer",
            "description": "ETL ve backend surecleri",
            "min_years_experience": 2,
            "required_skills": ["python", "sql", "docker"],
        },
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json["id"]


def _upload(client, candidate_id: int, job_id: int, content: bytes, headers):
    resp = client.post(
        "/api/v1/applications/upload",
        data={
            "candidate_id": str(candidate_id),
            "job_posting_id": str(job_id),
            "cv_file": (BytesIO(content), "cv.pdf"),
        },
        content_type="multipart/form-data",
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json


def test_job_summary_report() -> None:
    client = app.test_client()
    hr_headers = create_hr_headers(client)

    job_id = _create_job(client, hr_headers)
    candidate_1, _, candidate_1_headers, _, _ = create_candidate_with_headers(client, "Report Candidate One")
    candidate_2, _, candidate_2_headers, _, _ = create_candidate_with_headers(client, "Report Candidate Two")

    strong_cv = b"%PDF-1.4\nPython SQL Docker 5 year experience\n%%EOF\n"
    weak_cv = b"%PDF-1.4\nOnly random words 0 year\n%%EOF\n"

    strong_upload = _upload(client, candidate_1, job_id, strong_cv, candidate_1_headers)
    weak_upload = _upload(client, candidate_2, job_id, weak_cv, candidate_2_headers)

    assert strong_upload["match_score"] >= weak_upload["match_score"]

    summary_resp = client.get(f"/api/v1/reports/jobs/{job_id}/summary", headers=hr_headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json

    assert summary["applications_count"] >= 2
    assert summary["scored_count"] >= 2
    assert summary["max_score"] >= summary["min_score"]
    assert 0 <= summary["invitation_rate_percent"] <= 100


def test_overview_report() -> None:
    client = app.test_client()
    hr_headers = create_hr_headers(client)

    resp = client.get("/api/v1/reports/overview", headers=hr_headers)
    assert resp.status_code == 200
    body = resp.json

    assert "total_jobs" in body
    assert "total_candidates" in body
    assert "total_applications" in body
    assert "total_invitations" in body
    assert "avg_score_all" in body
