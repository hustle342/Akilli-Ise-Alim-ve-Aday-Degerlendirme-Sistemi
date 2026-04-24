# Akilli Ise Alim ve Aday Degerlendirme Sistemi

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
- Backend: FastAPI (Python)
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
- flask --app backend/app/main.py run --debug --port 8000
- set PYTHONPATH=backend && pytest backend/tests -q

## Ilk MileStone (MVP)
- Aday kaydi ve CV yukleme endpointleri
- Ilan olusturma endpointleri
- Basit kural tabanli uyum skoru endpointi
- Aday/ilan skorlama sonucunu listeleme

## Not
Bu repo ilk kurulum asamasindadir. Sonraki adimda veritabani modelleri, auth ve NLP pipeline katmani eklenecektir.
