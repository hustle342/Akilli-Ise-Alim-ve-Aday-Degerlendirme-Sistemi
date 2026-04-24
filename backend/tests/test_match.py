from app.main import app


def test_match_endpoint_returns_score_and_reasons() -> None:
    client = app.test_client()

    payload = {
        "candidate": {
            "name": "Aday Test",
            "years_experience": 3,
            "skills": ["python", "fastapi", "postgresql"],
            "education_level": "lisans"
        },
        "job": {
            "title": "Backend Developer",
            "min_years_experience": 2,
            "required_skills": ["python", "fastapi", "docker"]
        }
    }

    response = client.post("/api/v1/match", json=payload)

    assert response.status_code == 200
    body = response.json
    assert "score" in body
    assert "reasons" in body
    assert isinstance(body["reasons"], list)
