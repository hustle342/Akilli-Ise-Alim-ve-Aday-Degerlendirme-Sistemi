"""
Kabul Testleri – Akilli Ise Alim ve Aday Degerlendirme Sistemi
Hazirlayan: Serdar Korkmaz (Test Uzmani & Dokumantasyon Sorumlusu)

Bu dosya, sistemin uc-uca (end-to-end) kabul senaryolarini icerir.
Her test, PDF gereksinim belgesindeki bir is akisi asamasina karsilik gelir:

  FASE-1: Aday Kaydi ve Giris
  FASE-2: Ilan Olusturma (HR)
  FASE-3: CV Yukleme ve Otomatik Eslestirme
  FASE-4: Skor Siralama ve Kisaltilmis Liste
  FASE-5: Otomatik Davet Akisi
  FASE-6: Sistem Izleme (Audit Log / Raporlar)
"""

from io import BytesIO
from uuid import uuid4

import pytest

from app.main import app
from tests.auth_helpers import (
    create_admin_headers,
    create_candidate_with_headers,
    create_hr_headers,
)

# ---------------------------------------------------------------------------
# Yardimci sabitler ve fixture
# ---------------------------------------------------------------------------

STRONG_CV = (
    b"%PDF-1.4\n"
    b"Deneyimli Python Flask SQL Docker Kubernetes gelistirici\n"
    b"5 year experience backend API microservices\n"
    b"%%EOF\n"
)

WEAK_CV = (
    b"%PDF-1.4\n"
    b"Grafik tasarim ve fotograf duzenleme\n"
    b"0 year experience\n"
    b"%%EOF\n"
)


@pytest.fixture()
def client():
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# FASE-1: Aday Kaydi ve Kimlik Dogrulama
# ---------------------------------------------------------------------------


class TestFase1AdayKaydiVeGiris:
    """Aday sisteme kaydolabilmeli ve JWT ile oturum acabilmelidir."""

    def test_aday_kayit_ve_giris_basarili(self, client):
        """AC-1.1 – Aday e-posta + sifre ile kaydolur, token alir."""
        email = f"aday_{uuid4().hex[:8]}@test.com"
        password = "TestAday123!"

        reg = client.post(
            "/api/v1/candidates",
            json={"full_name": "Ahmet Aday", "email": email, "password": password},
        )
        assert reg.status_code == 201
        assert reg.json["email"] == email

        token_resp = client.post(
            "/api/v1/auth/token", json={"email": email, "password": password}
        )
        assert token_resp.status_code == 200
        body = token_resp.json
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["user"]["role"] == "candidate"

    def test_yanlis_sifre_ile_giris_reddedilir(self, client):
        """AC-1.2 – Yanlis sifre ile giris denemesi 401 doner."""
        email = f"aday_{uuid4().hex[:8]}@test.com"
        client.post(
            "/api/v1/candidates",
            json={"full_name": "Aday Test", "email": email, "password": "Dogru123!"},
        )
        resp = client.post(
            "/api/v1/auth/token",
            json={"email": email, "password": "YanlisSifre999!"},
        )
        assert resp.status_code == 401

    def test_refresh_token_yeni_access_token_uretir(self, client):
        """AC-1.3 – Refresh token kullanilarak yeni access token uretilir."""
        _, _, _, _, refresh = create_candidate_with_headers(client, "Refresh Aday")
        resp = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh}
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json

    def test_admin_bootstrap_kodu_ile_kayit(self, client):
        """AC-1.4 – Admin rol kaydi dogrulama koduyla gerceklesir."""
        email = f"admin_{uuid4().hex[:8]}@test.com"
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Test Admin",
                "email": email,
                "password": "Admin123!",
                "role": "admin",
                "bootstrap_code": "dev-bootstrap-code",
            },
        )
        assert resp.status_code == 201
        assert resp.json["role"] == "admin"

    def test_gecersiz_bootstrap_koduyla_admin_kayit_reddedilir(self, client):
        """AC-1.5 – Yanlis bootstrap kodu admin kaydini engeller."""
        email = f"fake_admin_{uuid4().hex[:8]}@test.com"
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Sahte Admin",
                "email": email,
                "password": "Admin123!",
                "role": "admin",
                "bootstrap_code": "YANLIS-KOD",
            },
        )
        assert resp.status_code in (400, 403)


# ---------------------------------------------------------------------------
# FASE-2: Ilan Olusturma (HR Rolü)
# ---------------------------------------------------------------------------


class TestFase2IlanOlusturma:
    """HR kullanicisi is ilani olusturabilmeli; aday olusturamamalidir."""

    def test_hr_ilan_olusturabilir(self, client):
        """AC-2.1 – HR rolü yeni is ilani olusturabilir."""
        hr_headers = create_hr_headers(client)
        resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "Python Backend Developer",
                "description": "Flask, SQL, REST API gelistirme",
                "min_years_experience": 2,
                "required_skills": ["python", "flask", "sql"],
            },
            headers=hr_headers,
        )
        assert resp.status_code == 201
        body = resp.json
        assert body["title"] == "Python Backend Developer"
        assert "id" in body

    def test_aday_ilan_olusturamaz(self, client):
        """AC-2.2 – Candidate rolü is ilani olusturamaz (403)."""
        _, _, cand_headers, _, _ = create_candidate_with_headers(client, "Yetkisiz Aday")
        resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "Yetkisiz Ilan",
                "description": "...",
                "min_years_experience": 0,
                "required_skills": [],
            },
            headers=cand_headers,
        )
        assert resp.status_code == 403

    def test_token_olmadan_ilan_olusturulamaz(self, client):
        """AC-2.3 – Token olmadan korunan endpoint 401 doner."""
        resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "Tokensiz Ilan",
                "description": "...",
                "min_years_experience": 0,
                "required_skills": [],
            },
        )
        assert resp.status_code == 401

    def test_ilan_listesi_herkes_tarafindan_gorulur(self, client):
        """AC-2.4 – Tum yetkili roller ilan listesini gorebilir."""
        hr_headers = create_hr_headers(client)
        client.post(
            "/api/v1/jobs",
            json={
                "title": "Listeleme Testi Ilani",
                "description": "test",
                "min_years_experience": 1,
                "required_skills": ["python"],
            },
            headers=hr_headers,
        )
        resp = client.get("/api/v1/jobs", headers=hr_headers)
        assert resp.status_code == 200
        jobs = resp.json["jobs"]
        assert isinstance(jobs, list)
        assert len(jobs) >= 1


# ---------------------------------------------------------------------------
# FASE-3: CV Yukleme ve Otomatik Eslestirme
# ---------------------------------------------------------------------------


class TestFase3CvYuklemeVeEslestirme:
    """Aday CV yukleyebilmeli; sistem otomatik skor uretmelidir."""

    def _create_job(self, client, hr_headers) -> int:
        resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "Backend Dev",
                "description": "Python Flask SQL",
                "min_years_experience": 2,
                "required_skills": ["python", "flask", "sql"],
            },
            headers=hr_headers,
        )
        return resp.json["id"]

    def test_aday_cv_yukler_ve_skor_alir(self, client):
        """AC-3.1 – Aday CV yukler; sistem 0-100 arasinda skor doner."""
        hr_headers = create_hr_headers(client)
        job_id = self._create_job(client, hr_headers)
        cand_id, _, cand_headers, _, _ = create_candidate_with_headers(client, "CV Aday")

        resp = client.post(
            "/api/v1/applications/upload",
            data={
                "candidate_id": str(cand_id),
                "job_posting_id": str(job_id),
                "cv_file": (BytesIO(STRONG_CV), "cv.pdf"),
            },
            content_type="multipart/form-data",
            headers=cand_headers,
        )
        assert resp.status_code == 201
        body = resp.json
        assert "match_score" in body
        assert 0 <= body["match_score"] <= 100
        assert "application_id" in body

    def test_guclu_cv_zayif_cvden_yuksek_skor_alir(self, client):
        """AC-3.2 – Ilana uygun CV daha yuksek skor almalidir."""
        hr_headers = create_hr_headers(client)
        job_id = self._create_job(client, hr_headers)

        strong_id, _, strong_h, _, _ = create_candidate_with_headers(client, "Guclu Aday")
        weak_id, _, weak_h, _, _ = create_candidate_with_headers(client, "Zayif Aday")

        def upload(cid, headers, content):
            r = client.post(
                "/api/v1/applications/upload",
                data={
                    "candidate_id": str(cid),
                    "job_posting_id": str(job_id),
                    "cv_file": (BytesIO(content), "cv.pdf"),
                },
                content_type="multipart/form-data",
                headers=headers,
            )
            assert r.status_code == 201
            return r.json["match_score"]

        strong_score = upload(strong_id, strong_h, STRONG_CV)
        weak_score = upload(weak_id, weak_h, WEAK_CV)
        assert strong_score > weak_score

    def test_baska_aday_adina_cv_yuklenemez(self, client):
        """AC-3.3 – Aday yalnizca kendi id'si ile CV yukleyebilir (403)."""
        hr_headers = create_hr_headers(client)
        job_id = self._create_job(client, hr_headers)

        id_a, _, headers_a, _, _ = create_candidate_with_headers(client, "Aday A")
        id_b, _, _, _, _ = create_candidate_with_headers(client, "Aday B")

        resp = client.post(
            "/api/v1/applications/upload",
            data={
                "candidate_id": str(id_b),  # B'nin id'si ile A'nin tokeni
                "job_posting_id": str(job_id),
                "cv_file": (BytesIO(STRONG_CV), "cv.pdf"),
            },
            content_type="multipart/form-data",
            headers=headers_a,
        )
        assert resp.status_code == 403

    def test_aday_kendi_basvurularini_listeler(self, client):
        """AC-3.4 – Aday /applications/me ile kendi basvurularini gorebilir."""
        hr_headers = create_hr_headers(client)
        job_id = self._create_job(client, hr_headers)
        cand_id, _, cand_headers, _, _ = create_candidate_with_headers(client, "Liste Aday")

        client.post(
            "/api/v1/applications/upload",
            data={
                "candidate_id": str(cand_id),
                "job_posting_id": str(job_id),
                "cv_file": (BytesIO(STRONG_CV), "cv.pdf"),
            },
            content_type="multipart/form-data",
            headers=cand_headers,
        )

        resp = client.get("/api/v1/applications/me", headers=cand_headers)
        assert resp.status_code == 200
        apps = resp.json["applications"]
        assert isinstance(apps, list)
        assert len(apps) >= 1


# ---------------------------------------------------------------------------
# FASE-4: Skor Siralama ve Kisaltilmis Liste
# ---------------------------------------------------------------------------


class TestFase4SkorSiralamaVeKisaltilmisListe:
    """HR, adaylari skora gore siralayabilmeli ve es deger filtre uygulayabilmelidir."""

    def _prepare(self, client):
        """HR + ilan + 2 aday (guclu/zayif) olustur."""
        hr_headers = create_hr_headers(client)
        resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "Siralama Testi",
                "description": "python flask sql",
                "min_years_experience": 1,
                "required_skills": ["python", "flask", "sql"],
            },
            headers=hr_headers,
        )
        job_id = resp.json["id"]

        strong_id, _, sh, _, _ = create_candidate_with_headers(client, "S1 Strong")
        weak_id, _, wh, _, _ = create_candidate_with_headers(client, "S1 Weak")

        for cid, headers, cv in [
            (strong_id, sh, STRONG_CV),
            (weak_id, wh, WEAK_CV),
        ]:
            client.post(
                "/api/v1/applications/upload",
                data={
                    "candidate_id": str(cid),
                    "job_posting_id": str(job_id),
                    "cv_file": (BytesIO(cv), "cv.pdf"),
                },
                content_type="multipart/form-data",
                headers=headers,
            )

        return job_id, hr_headers

    def test_aday_listesi_skora_gore_sirali_gelir(self, client):
        """AC-4.1 – /jobs/{id}/candidates listesi skora gore azalan sirada gelir."""
        job_id, hr_headers = self._prepare(client)
        resp = client.get(f"/api/v1/jobs/{job_id}/candidates", headers=hr_headers)
        assert resp.status_code == 200
        candidates = resp.json["candidates"]
        scores = [c["match_score"] for c in candidates]
        assert scores == sorted(scores, reverse=True)

    def test_kisaltilmis_listede_yalnizca_esik_ustu_adaylar_var(self, client):
        """AC-4.2 – /shortlisted?threshold=70 yalnizca >=70 skoru olan adaylari doner."""
        job_id, hr_headers = self._prepare(client)
        resp = client.get(
            f"/api/v1/jobs/{job_id}/shortlisted?threshold=70", headers=hr_headers
        )
        assert resp.status_code == 200
        for item in resp.json["candidates"]:
            assert item["score"] >= 70

    def test_sifir_esikli_kisa_liste_tum_adaylari_icerir(self, client):
        """AC-4.3 – threshold=0 iken tum adaylar kisaltilmis listede yer alir."""
        job_id, hr_headers = self._prepare(client)
        resp = client.get(
            f"/api/v1/jobs/{job_id}/shortlisted?threshold=0", headers=hr_headers
        )
        assert resp.status_code == 200
        assert resp.json["shortlisted_count"] >= 2


# ---------------------------------------------------------------------------
# FASE-5: Otomatik Davet Akisi
# ---------------------------------------------------------------------------


class TestFase5OtomatikDavetAkisi:
    """Yuksek skorlu adaylar otomatik davet alabilmeli; HR davetleri listeleyebilmelidir."""

    def test_yuksek_skorlu_aday_otomatik_davet_alir(self, client):
        """AC-5.1 – AUTO_INVITE_SCORE_THRESHOLD (70) ustu skor otomatik davet olusturur."""
        hr_headers = create_hr_headers(client)
        resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "Davet Testi",
                "description": "python flask sql",
                "min_years_experience": 1,
                "required_skills": ["python", "flask", "sql"],
            },
            headers=hr_headers,
        )
        job_id = resp.json["id"]

        cand_id, cand_email, cand_headers, _, _ = create_candidate_with_headers(client, "Davet Aday")
        upload = client.post(
            "/api/v1/applications/upload",
            data={
                "candidate_id": str(cand_id),
                "job_posting_id": str(job_id),
                "cv_file": (BytesIO(STRONG_CV), "cv.pdf"),
            },
            content_type="multipart/form-data",
            headers=cand_headers,
        )
        score = upload.json["match_score"]

        inv_resp = client.get(
            f"/api/v1/invitations?job_posting_id={job_id}", headers=hr_headers
        )
        assert inv_resp.status_code == 200
        invitations = inv_resp.json["invitations"]

        if score >= 70:
            assert len(invitations) >= 1
            assert any(inv["candidate_email"] == cand_email for inv in invitations)

    def test_davet_listesi_job_id_ile_filtrelenir(self, client):
        """AC-5.2 – Davet listesi job_posting_id parametresi ile filtrelenebilir."""
        hr_headers = create_hr_headers(client)

        def make_job(title):
            r = client.post(
                "/api/v1/jobs",
                json={
                    "title": title,
                    "description": "python flask sql",
                    "min_years_experience": 1,
                    "required_skills": ["python", "flask"],
                },
                headers=hr_headers,
            )
            return r.json["id"]

        job_a = make_job("Davet Filtre A")
        job_b = make_job("Davet Filtre B")

        cid, _, ch, _, _ = create_candidate_with_headers(client, "Filtre Aday")
        client.post(
            "/api/v1/applications/upload",
            data={
                "candidate_id": str(cid),
                "job_posting_id": str(job_a),
                "cv_file": (BytesIO(STRONG_CV), "cv.pdf"),
            },
            content_type="multipart/form-data",
            headers=ch,
        )

        resp_b = client.get(
            f"/api/v1/invitations?job_posting_id={job_b}", headers=hr_headers
        )
        assert resp_b.status_code == 200
        # Yalnizca job_a'ya yuklendi; job_b'de davet olmamali
        for inv in resp_b.json["invitations"]:
            assert inv["job_posting_id"] == job_b


# ---------------------------------------------------------------------------
# FASE-6: Sistem Izleme – Raporlar ve Audit Log
# ---------------------------------------------------------------------------


class TestFase6SistemIzleme:
    """Admin/HR raporlara erisebilmeli; admin audit loglari gorebilmelidir."""

    def test_genel_ozet_raporu_donus_yapar(self, client):
        """AC-6.1 – /reports/overview temel metrik alanlarini doner."""
        hr_headers = create_hr_headers(client)
        resp = client.get("/api/v1/reports/overview", headers=hr_headers)
        assert resp.status_code == 200
        body = resp.json
        for key in ("total_jobs", "total_applications", "total_candidates"):
            assert key in body

    def test_ilan_ozeti_raporu_donus_yapar(self, client):
        """AC-6.2 – /reports/jobs/{id}/summary ilan bazli metrikleri doner."""
        hr_headers = create_hr_headers(client)
        resp = client.post(
            "/api/v1/jobs",
            json={
                "title": "Rapor Test Ilani",
                "description": "python flask sql",
                "min_years_experience": 1,
                "required_skills": ["python"],
            },
            headers=hr_headers,
        )
        job_id = resp.json["id"]

        summary = client.get(
            f"/api/v1/reports/jobs/{job_id}/summary", headers=hr_headers
        )
        assert summary.status_code == 200
        body = summary.json
        for key in ("job_posting_id", "applications_count", "avg_score"):
            assert key in body

    def test_admin_audit_log_erisebilir(self, client):
        """AC-6.3 – Admin audit log listesini gorebilir."""
        admin_headers = create_admin_headers(client)
        resp = client.get("/api/v1/audit-logs", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json["logs"], list)

    def test_aday_audit_log_erisemez(self, client):
        """AC-6.4 – Candidate rolü audit log'a erisemez (403)."""
        _, _, cand_headers, _, _ = create_candidate_with_headers(client, "Audit Aday")
        resp = client.get("/api/v1/audit-logs", headers=cand_headers)
        assert resp.status_code == 403

    def test_audit_log_path_filtresi(self, client):
        """AC-6.5 – Audit log path parametresi ile filtrelenebilir."""
        admin_headers = create_admin_headers(client)
        # Once bir istek at ki logda gorgunsun
        client.get("/api/v1/reports/overview", headers=admin_headers)

        resp = client.get(
            "/api/v1/audit-logs?path=/api/v1/reports/overview", headers=admin_headers
        )
        assert resp.status_code == 200
        for entry in resp.json["logs"]:
            assert "/reports/overview" in entry["path"]
