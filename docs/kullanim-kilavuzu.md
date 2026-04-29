# Kullanım Kılavuzu — Akıllı İşe Alım ve Aday Değerlendirme Sistemi

**Hazırlayan:** Serdar Korkmaz (Test Uzmanı & Dokümantasyon Sorumlusu)  
**Sürüm:** 1.0  
**Tarih:** Nisan 2026

---

## İçindekiler

1. [Sistem Gereksinimleri](#1-sistem-gereksinimleri)
2. [Kurulum ve Başlatma](#2-kurulum-ve-başlatma)
3. [Demo Hesapları](#3-demo-hesapları)
4. [Aday Kullanım Akışı](#4-aday-kullanım-akışı)
5. [İK (HR) Kullanım Akışı](#5-i̇k-hr-kullanım-akışı)
6. [Admin Kullanım Akışı](#6-admin-kullanım-akışı)
7. [Mobil Uygulama](#7-mobil-uygulama)
8. [API Referans Özeti](#8-api-referans-özeti)
9. [Sık Karşılaşılan Sorunlar](#9-sık-karşılaşılan-sorunlar)

---

## 1. Sistem Gereksinimleri

| Bileşen | Minimum Sürüm |
|---------|--------------|
| Python  | 3.10+        |
| Flutter | 3.19+        |
| SQLite  | (dahili, kurulum gerektirmez) |
| RAM     | 512 MB       |

---

## 2. Kurulum ve Başlatma

### 2.1 Backend

```powershell
# Proje dizinine gir
cd C:\Users\Serdar\Desktop\CevriyeOdev

# Sanal ortam oluştur ve bağımlılıkları kur
python -m venv .venv
.venv\Scripts\pip install -r backend\requirements.txt

# Backend'i başlat (PowerShell)
$env:PYTHONPATH='backend'
& ".venv\Scripts\python.exe" -m flask --app app.main run --debug --port 8000
```

Başarılı başlatmada konsolda şu mesaj görünür:

```
 * Running on http://127.0.0.1:8000
 * Debug mode: on
```

### 2.2 Demo Verisi Yükleme (İsteğe Bağlı)

```powershell
$env:PYTHONPATH='backend'
& ".venv\Scripts\python.exe" backend\scripts\seed_data.py
```

Bu komut 8 kullanıcı, 3 iş ilanı ve 7 başvuru oluşturur.

### 2.3 Testleri Çalıştırma

```powershell
$env:PYTHONPATH='c:\Users\Serdar\Desktop\CevriyeOdev\backend'
& ".venv\Scripts\python.exe" -m pytest backend\tests -q
```

Beklenen çıktı: **40 passed** (17 birim + 23 kabul testi)

### 2.4 Mobil Uygulama

```powershell
cd mobile_app
flutter pub get
flutter run -d chrome          # Web tarayıcıda
# veya
flutter run -d windows         # Windows masaüstü uygulaması
```

---

## 3. Demo Hesapları

Seed data yüklendikten sonra aşağıdaki hesapları kullanabilirsiniz:

| Rol       | E-posta                   | Şifre           |
|-----------|---------------------------|-----------------|
| Admin     | admin@demo.com            | AdminPass123!   |
| İK (HR)   | ayse.hr@demo.com          | HrPass123!      |
| İK (HR)   | mehmet.hr@demo.com        | HrPass123!      |
| Aday      | ali@demo.com              | Candidate123!   |
| Aday      | fatma@demo.com            | Candidate123!   |
| Aday      | emre@demo.com             | Candidate123!   |
| Aday      | zeynep@demo.com           | Candidate123!   |
| Aday      | can@demo.com              | Candidate123!   |

> **Not:** Yeni kullanıcı oluşturmak için bootstrap kodu: `dev-bootstrap-code`

---

## 4. Aday Kullanım Akışı

### Adım 1 — Kayıt

```http
POST /api/v1/candidates
Content-Type: application/json

{
  "full_name": "Ad Soyad",
  "email": "aday@example.com",
  "password": "Sifre123!"
}
```

Başarılı yanıt (201):
```json
{ "id": 42, "email": "aday@example.com", "role": "candidate" }
```

### Adım 2 — Giriş ve Token Alma

```http
POST /api/v1/auth/token
Content-Type: application/json

{
  "email": "aday@example.com",
  "password": "Sifre123!"
}
```

Yanıt:
```json
{
  "access_token": "<JWT>",
  "refresh_token": "<JWT>",
  "token_type": "bearer",
  "user": { "id": 42, "email": "aday@example.com", "role": "candidate" }
}
```

Sonraki tüm isteklerde header olarak ekleyin:
```
Authorization: Bearer <access_token>
```

### Adım 3 — İlanları Görüntüleme

```http
GET /api/v1/jobs
Authorization: Bearer <token>
```

Yanıt `jobs` dizisini döner; her ilandaki `required_skills` ve `min_years_experience` değerlerine göre CV'nizi hazırlayabilirsiniz.

### Adım 4 — CV Yükleme ve Başvuru

```http
POST /api/v1/applications/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

candidate_id: <kendi_id'niz>
job_posting_id: <ilan_id>
cv_file: <PDF dosyası>
```

Yanıt:
```json
{
  "application_id": 15,
  "match_score": 85.0,
  "auto_invited": true
}
```

- `match_score` 0–100 arası otomatik hesaplanır.
- `auto_invited: true` ise sisteminize davet kaydı oluşturulmuştur.

### Adım 5 — Başvurularımı Görüntüleme

```http
GET /api/v1/applications/me
Authorization: Bearer <token>
```

---

## 5. İK (HR) Kullanım Akışı

### İK Hesabı Oluşturma

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "full_name": "İK Kullanıcı",
  "email": "ik@sirket.com",
  "password": "HrPass123!",
  "role": "hr",
  "bootstrap_code": "dev-bootstrap-code"
}
```

### İlan Oluşturma

```http
POST /api/v1/jobs
Authorization: Bearer <hr_token>
Content-Type: application/json

{
  "title": "Python Backend Developer",
  "description": "REST API ve veritabanı geliştirme",
  "min_years_experience": 2,
  "required_skills": ["python", "flask", "sql"]
}
```

### Başvuru Listesi ve Skorlama

```http
GET /api/v1/jobs/{job_id}/candidates
Authorization: Bearer <hr_token>
```

Adaylar `match_score`'a göre azalan sırayla gelir.

### Kısaltılmış Liste (Shortlist)

```http
GET /api/v1/jobs/{job_id}/shortlisted?threshold=70
Authorization: Bearer <hr_token>
```

Yalnızca eşik üstü (varsayılan: 70) adayları listeler.

### Davetleri Görüntüleme

```http
GET /api/v1/invitations?job_posting_id={job_id}
Authorization: Bearer <hr_token>
```

İsteğe bağlı filtreler:
- `status=sent` — gönderilmiş davetler
- `job_posting_id={id}` — ilan bazlı filtreleme

### İlan Raporu

```http
GET /api/v1/reports/jobs/{job_id}/summary
Authorization: Bearer <hr_token>
```

Dönen alanlar: `applications_count`, `avg_score`, `max_score`, `min_score`, `invitation_count`, `invitation_rate_percent`

### Genel Sistem Raporu

```http
GET /api/v1/reports/overview
Authorization: Bearer <hr_token>
```

---

## 6. Admin Kullanım Akışı

Admin tüm İK yetkilerine ek olarak aşağıdaki işlemleri yapabilir:

### Audit Log Görüntüleme

```http
GET /api/v1/audit-logs
Authorization: Bearer <admin_token>
```

Opsiyonel filtreler:
- `path=/api/v1/jobs` — endpoint bazlı filtreleme
- `method=POST` — HTTP metod filtresi
- `limit=100` — sonuç sayısı (maks: 200)

Her log kaydında: `user_id`, `role`, `method`, `path`, `status_code`, `ip_address` bulunur.

### Token Yenileme

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{ "refresh_token": "<refresh_token>" }
```

---

## 7. Mobil Uygulama

Uygulama açıldığında aşağıdaki ekranlar rol bazlı olarak sunulur:

| Rol       | Ekranlar |
|-----------|---------|
| Candidate | Giriş, Dashboard (aktif başvurular, CV yükleme) |
| HR        | Giriş, İlan Yönetimi, Aday Listesi, Shortlist/Davetler |
| Admin     | Giriş, Genel Bakış Raporu, Audit Log |

**Backend URL Ayarı:**
- Web/Windows: `http://127.0.0.1:8000`
- Android Emulator: `http://10.0.2.2:8000`

Uygulama içinde "Ayarlar" ikonundan backend URL'i değiştirilebilir.

---

## 8. API Referans Özeti

| Endpoint | Metod | Yetki | Açıklama |
|----------|-------|-------|---------|
| `/api/v1/candidates` | POST | — | Aday kaydı |
| `/api/v1/auth/register` | POST | bootstrap_code | HR/Admin kaydı |
| `/api/v1/auth/token` | POST | — | Giriş, token üretir |
| `/api/v1/auth/refresh` | POST | — | Access token yeniler |
| `/api/v1/jobs` | GET | hr/admin/candidate | İlan listesi |
| `/api/v1/jobs` | POST | hr/admin | İlan oluşturma |
| `/api/v1/applications/upload` | POST | candidate/admin | CV yükleme + puanlama |
| `/api/v1/applications/me` | GET | candidate/admin | Kendi başvurularım |
| `/api/v1/jobs/{id}/candidates` | GET | hr/admin | İlan bazlı aday listesi |
| `/api/v1/jobs/{id}/shortlisted` | GET | hr/admin | Kısaltılmış liste |
| `/api/v1/invitations` | GET | hr/admin | Davet listesi |
| `/api/v1/reports/overview` | GET | hr/admin | Genel rapor |
| `/api/v1/reports/jobs/{id}/summary` | GET | hr/admin | İlan özet raporu |
| `/api/v1/audit-logs` | GET | admin | İstek logları |

---

## 9. Sık Karşılaşılan Sorunlar

### Backend başlamıyor

```
ModuleNotFoundError: No module named 'app'
```
**Çözüm:** `PYTHONPATH` değişkenini `backend` klasörüne ayarlayın:
```powershell
$env:PYTHONPATH='backend'
```

### 401 Unauthorized Hatası

Token süresi dolmuş olabilir. Refresh token ile yeni access token alın:
```http
POST /api/v1/auth/refresh
{ "refresh_token": "<refresh_token>" }
```

### 403 Forbidden Hatası

İstek yapılan endpoint'e rolünüz erişim iznine sahip değil. Örneğin:
- Candidate rolü `/api/v1/jobs` POST yapamaz
- Candidate rolü `/api/v1/audit-logs` GET yapamaz

### CV Skoru Beklenenden Düşük

Skor hesaplama kuralı:
- **Beceri eşleşmesi (70 puan):** CV metninde ilana ait `required_skills` kelimeleri aranır.
- **Deneyim (30 puan):** CV'deki "X year(s) experience" ifadesi ile `min_years_experience` karşılaştırılır.

CV'nizde ilgili anahtar kelimelerin açıkça geçtiğinden emin olun.

### Flutter Bağlantı Hatası

Android emülatöründe `127.0.0.1` çalışmaz. Backend URL olarak `http://10.0.2.2:8000` kullanın.

---

*Bu kılavuz sistem kullanımına yönelik pratik bir rehber niteliğindedir. Teknik mimari için `docs/architecture.md`, veri modeli için `docs/data-model.md` belgesine bakınız.*
