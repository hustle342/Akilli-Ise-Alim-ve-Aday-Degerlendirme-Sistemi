# Akilli Ise Alim ve Aday Degerlendirme Sistemi

---

## 📊 Proje Tamamlanma Durumu

> **Genel İlerleme: %75**

```
██████████████████████░░░░░░  75%
```

| Alan | Durum | % |
|------|-------|---|
| Backend API (tüm endpoint'ler) | ✅ Tamamlandı | %100 |
| Kimlik Doğrulama & Yetkilendirme (JWT, RBAC) | ✅ Tamamlandı | %100 |
| CV Parsing (pypdf, kural tabanlı) | ✅ Tamamlandı | %100 |
| Uyum Skoru (kural tabanlı) | ✅ Tamamlandı | %100 |
| Flutter Mobil Uygulama | ✅ Büyük ölçüde tamamlandı | %70 |
| Veritabanı Modelleri (SQLite/SQLAlchemy) | ✅ Tamamlandı | %100 |
| Test Altyapısı (40 test) | ✅ Tamamlandı | %100 |
| Dokümantasyon | ✅ Tamamlandı | %100 |
| AI/NLP (spaCy, BERT/sentence-transformers) | ❌ Yapılmadı | %0 |
| PostgreSQL Geçişi | ❌ Yapılmadı | %0 |
| Redis Önbellekleme | ❌ Yapılmadı | %0 |
| Docker Production Ayarları | ❌ Yapılmadı | %0 |
| Figma UI/UX Tasarımları | ❌ Yapılmadı | %0 |
| Final Rapor & Sunum Materyalleri | ❌ Yapılmadı | %0 |

---

## 👥 Üye Katkı Oranları

| # | Üye | Rol | Katkı |
|---|-----|-----|-------|
| 1 | Sıtkı Efe Kılınç | Proje Yöneticisi & Backend Geliştirici | **%0** |
| 2 | Zeynep Sütçü | AI/NLP Uzmanı | **%0** |
| 3 | Ecem Nur Durak | Mobil/Frontend Geliştirici (Flutter) | **%0** |
| 4 | Samet Tanay | Veritabanı Mimarı & API Entegrasyon | **%0** |
| 5 | Serdar Korkmaz | Test Uzmanı & Dokümantasyon Sorumlusu | **%130** |

> Serdar Korkmaz projedeki tüm geliştirme, test ve dokümantasyon çalışmalarını tek başına yürütmüştür. Diğer üyeler henüz projeye katkı sağlamamıştır.

---

## ✅❌ Üye Görev Listeleri

### 1 — Sıtkı Efe Kılınç · Proje Yöneticisi & Backend Geliştirici

- ❌ Flask uygulama fabrikası ve blueprint yapısı
- ❌ REST API endpoint'leri (auth, jobs, applications, invitations, reports)
- ❌ JWT tabanlı kimlik doğrulama (access + refresh token)
- ❌ Rol tabanlı erişim kontrolü (`@require_roles` dekoratörü)
- ❌ CV upload & otomatik parse akışı
- ❌ Otomatik davet mekanizması (eşik skoru: 70)
- ❌ Audit log middleware (tüm HTTP istekleri loglanıyor)
- ❌ spaCy / NLTK NLP entegrasyonu
- ❌ Docker production konfigürasyonu (Dockerfile, compose güncelleme)
- ❌ Final demo sunumu ve proje yönetimi raporlaması

---

### 2 — Zeynep Sütçü · AI/NLP Uzmanı (CV Parsing & Skorlama)

- ❌ PDF metin çıkarma (pypdf kütüphanesi)
- ❌ Kural tabanlı beceri eşleştirme (required_skills vs CV metni)
- ❌ Deneyim yılı tahmini (regex tabanlı)
- ❌ 0-100 uyum skoru hesaplama (beceri %70 + deneyim %30)
- ❌ spaCy NLP pipeline (lemmatization, NER)
- ❌ Sentence-transformers (BERT/RoBERTa) semantik skorlama
- ❌ Model doğruluk ölçümleri ve optimizasyonu
- ❌ Çok dilli CV desteği

---

### 3 — Ecem Nur Durak · Mobil/Frontend Geliştirici (Flutter)

- ❌ Flutter uygulama iskeleti (multi-platform: web, Windows, Android)
- ❌ Auth ekranı (kayıt & giriş)
- ❌ Rol tabanlı dashboard (candidate / HR / admin)
- ❌ Candidate: aktif başvurular ve CV yükleme ekranı
- ❌ HR: ilan oluşturma ve aday listeleme ekranı
- ❌ HR: shortlist ve davet yönetimi ekranı
- ❌ Admin: genel bakış raporu ve audit log ekranı
- ❌ Figma UI/UX tasarım dosyaları
- ❌ Uygulama ikonu, splash screen ve tema sistemi
- ❌ Android / iOS fiziksel cihaz build testi

---

### 4 — Samet Tanay · Veritabanı Mimarı & API Entegrasyon Sorumlusu

- ❌ SQLAlchemy 2.0 ORM modelleri (User, JobPosting, Application, MatchScore, Invitation, AuditLog)
- ❌ SQLite veritabanı (geliştirme ortamı)
- ❌ Otomatik tablo oluşturma ve şema güncelleme (`ensure_schema`)
- ❌ Demo verisi seed scripti (8 kullanıcı, 3 ilan, 7 başvuru)
- ❌ docker-compose.yml taslağı
- ❌ PostgreSQL'e geçiş ve üretim ortamı yapılandırması
- ❌ Redis önbellek entegrasyonu
- ❌ Alembic ile veritabanı migration yönetimi

---

### 5 — Serdar Korkmaz · Test Uzmanı & Dokümantasyon Sorumlusu

- ✅ Birim testleri — 17 test (`test_health`, `test_models`, `test_match`, `test_auth_rbac`, vb.)
- ✅ Kabul testleri — 23 test, 6 fazda (`test_acceptance.py`)
- ✅ `docs/requirements.md` — Gereksinim dokümanı
- ✅ `docs/architecture.md` — Mimari doküman
- ✅ `docs/data-model.md` — Veri modeli dokümanı
- ✅ `docs/roadmap.md` — Yol haritası
- ✅ `docs/uml-diagrams.md` — UML diyagramları (Class, Use Case, 2× Sequence)
- ✅ `docs/kullanim-kilavuzu.md` — Adım adım kullanım kılavuzu
- ✅ `docs/postman-collection.json` — Postman API koleksiyonu (tüm endpoint'ler + assertion'lar)
- ❌ Final rapor belgesi (proje sonu kapsamlı rapor)
- ❌ Sunum materyalleri (slayt / demo senaryosu)

---

Bu repo, Yazilim Tasarim ve Mimarisi icin planlanan yapay zeka destekli ise alim platformunun gelistirme calismasini icerir.

## Proje Ozeti
Sistem; aday CV'lerini analiz eder, ilan kriterleri ile eslestirir, uyum skoru uretir ve IK surecini uçtan uca dijitallestirir.

## Hedefler
- CV Parsing ile aday bilgisini standart formata donusturmek
- Ilan ve aday arasinda semantik benzerlik tabanli skor uretmek
- IK tarafinda karar destek paneli olusturmak
- Test/mulakat adimlarini otomatik tetiklemek

## Teknoloji Yaklasimi
- Mobil/Frontend: Flutter
- Backend: Flask (Python)
- AI/NLP: spaCy, sentence-transformers
- Veritabani: PostgreSQL
- Onbellek/Kuyruk: Redis
- Konteyner: Docker

## Mevcut Yapi
- docs/: Gereksinim, mimari ve yol haritasi dokumanlari
- backend/: API, servis katmani ve test altyapisi
- mobile_app/: Flutter tabanli mobil/web istemcisi

## Mobil Uygulama
- Flutter istemci `mobile_app` klasorundedir.
- Ilk surumde kayit, giris, rol bazli dashboard, candidate CV yukleme, HR ilan olusturma/aday listeleme ve admin audit log goruntuleme bulunur.
- Varsayilan backend adresi: `http://127.0.0.1:8000`
- Android emulator icin backend adresini genellikle `http://10.0.2.2:8000` yapman gerekir.

Ornek komutlar:
- `cd mobile_app`
- `flutter pub get`
- `flutter run -d chrome`
- veya `flutter run -d windows`

## API Uclari (Ilk Surum)
- POST /api/v1/auth/register: Password ile kullanici kaydi (candidate/hr/admin)
- POST /api/v1/auth/token: Email + password ile access/refresh token uretir
- POST /api/v1/auth/refresh: Refresh token ile yeni access token uretir
- POST /api/v1/candidates: Aday kaydi olusturur
- POST /api/v1/jobs: Ilan olusturur
- GET /api/v1/jobs: Candidate/hr/admin icin ilanlari listeler
- POST /api/v1/applications/upload: PDF CV yukler, parse eder ve basvuru kaydi acar
- GET /api/v1/applications/me: Adayin kendi basvurularini listeler
- POST /api/v1/match: Aday-ilan uyum skoru hesaplar
- GET /api/v1/jobs/{job_posting_id}/candidates: Ilan bazli adaylari skora gore listeler
- GET /api/v1/jobs/{job_posting_id}/shortlisted?threshold=70: Baraj ustu adaylari listeler
- GET /api/v1/invitations?status=sent&job_posting_id={id}: Davet kayitlarini filtreleyerek listeler
- GET /api/v1/reports/jobs/{job_posting_id}/summary: Ilan bazli ozet metrikler
- GET /api/v1/reports/overview: Sistem geneli metrik ozeti
- GET /api/v1/audit-logs?path=/health&method=GET: Admin icin istek loglarini listeler

## Yetkilendirme Notu
- Korumali endpointler Authorization: Bearer <token> bekler.
- Login akisi email-only degildir; kayit sirasinda password zorunludur.
- Access token korumali endpointlerde kullanilir, refresh token yalnizca /auth/refresh icindir.
- /jobs, /invitations ve /reports endpointleri yalnizca hr/admin rollerine aciktir.
- /audit-logs endpointi yalnizca admin rolune aciktir.
- /applications/upload endpointi candidate/admin rolleri ile calisir.
- Candidate rolunde oturum acan kullanici yalnizca kendi candidate_id degeriyle basvuru yukleyebilir.

## Izleme
- Tum HTTP istekleri merkezi audit log tablosuna yazilir.
- Log kaydinda kullanici, rol, method, path, status code ve IP bilgisi tutulur.

## Hizli Baslangic (Backend)
1. Sanal ortam olustur
2. Bagimliliklari kur
3. API'yi calistir

Ornek komutlar:
- pip install -r backend/requirements.txt
- set PYTHONPATH=backend && python backend/scripts/init_db.py
- set PYTHONPATH=backend && python -m flask --app app.main run --debug --port 8000
- set PYTHONPATH=backend && pytest backend/tests -q

## Ilk MileStone (MVP)
- Aday kaydi ve CV yukleme endpointleri
- Ilan olusturma endpointleri
- Basit kural tabanli uyum skoru endpointi
- Aday/ilan skorlama sonucunu listeleme

## Not
Bu repo artik ilk kurulum asamasini gecmistir. Backend MVP, mobil istemci iskeleti, auth, raporlama ve audit log katmanlari mevcuttur.
Sonraki adimlar daha cok calistirma/entegrasyon duzeltmeleri, ekran tamamlama ve final teslim hazirligidir.
