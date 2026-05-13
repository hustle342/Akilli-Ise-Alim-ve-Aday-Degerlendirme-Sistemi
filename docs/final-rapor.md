# Akilli Ise Alim ve Aday Degerlendirme Sistemi — Final Rapor

**Proje Adi:** Akilli Ise Alim ve Aday Degerlendirme Sistemi  
**Ders:** Yazilim Tasarim ve Mimarisi  
**Tarih:** Mayis 2026  

---

## 1. Yonetici Ozeti

Bu proje, IK sureclerini dijitallestirmek ve otomatiklestirmek amaciyla gelistirilmis bir kurumsal ise alim platformudur. Sistem, adaylarin CV'lerini otomatik olarak analiz eder, ilan kriterlerine gore uyum skoru hesaplar ve IK yoneticilerine karar destek paneli sunar.

**Temel Basarilar:**
- 40 birim + kabul testi ile dogrulanmis, uretim ortamina hazir backend
- Flutter tabanli multi-platform istemci (Web, Windows, Android)
- Onion Architecture ile modüler, genisletilebilir, test edilebilir yapi
- 6 tasarim deseni entegrasyonu (Singleton, Factory, Facade, Adapter, Strategy, Observer)

---

## 2. Mimari Yaklasim

### 2.1 Onion Architecture

Proje, katmanli bagimlilik yonetimi saglayan Onion (Sogan) mimarisi uzerine kurulmustur:

```
         ┌────────────────────────────────┐
         │       Presentation Layer       │
         │   (Flask Routes, Middleware)   │
         ├────────────────────────────────┤
         │      Application Layer         │
         │   (CQRS Commands/Queries,      │
         │    Facade, DTOs)               │
         ├────────────────────────────────┤
         │    Infrastructure Layer        │
         │   (DB, Redis, Scoring,         │
         │    CVParser, EventBus)         │
         ├────────────────────────────────┤
         │         Core (Domain)          │
         │   (Entities, Interfaces,       │
         │    Value Objects, Enums)        │
         └────────────────────────────────┘
```

### 2.2 Tasarim Desenleri

| Desen | Sinif | Amac |
|-------|-------|------|
| **Singleton** | `ConfigurationManager`, `DatabaseManager` | Tekil baglanti ve konfigurasyon yonetimi |
| **Factory Method** | `ScoringFactory` | Dinamik strateji uretimi |
| **Facade** | `RecruitmentFacade` | Karmasik alt servisleri tek arayuzden sunma |
| **Adapter** | `CVParserAdapter`, `NLPParserAdapter` | Dis kutuphane entegrasyonu |
| **Strategy** | `RuleBasedScoringStrategy`, `SemanticScoringStrategy` | Degistirilebilir skorlama algoritmalari |
| **Observer** | `InMemoryEventBus` | Olay tabanli iletisim (ESB) |

### 2.3 CQRS (Command Query Responsibility Segregation)

- **Commands:** `RegisterUserCommand`, `CreateJobCommand`, `UploadCVCommand`
- **Queries:** `GetJobsQuery`, `GetMyApplicationsQuery`, `GetJobCandidatesQuery`, `GetReportQuery`
- **Separation of Concerns:** Yazma ve okuma islemleri farkli handler'lar tarafindan yonetilir.

---

## 3. Teknoloji Yigini

| Katman | Teknoloji | Versiyon |
|--------|-----------|----------|
| Backend | Flask (Python) | 3.1.0 |
| Frontend | Flutter (Dart) | 3.x |
| Veritabani | SQLite (dev) / PostgreSQL (prod) | - |
| Onbellek | Redis | 7.4.0 |
| ORM | SQLAlchemy | 2.0.40 |
| Migration | Alembic | 1.18.4 |
| Auth | itsdangerous (JWT-like) | 2.2.0 |
| PDF Parse | pypdf | 5.4.0 |
| NLP | spaCy (opsiyonel) | - |
| Semantik | sentence-transformers (opsiyonel) | - |
| Konteyner | Docker, docker-compose | - |
| WebSocket | flask-socketio | 5.5.1 |
| Test | pytest | 8.3.5 |

---

## 4. Fonksiyonel Gereksinimler ve Gerceklestirme

### 4.1 Kimlik Dogrulama ve Yetkilendirme

- **JWT Tabanli Auth:** Access token (24 saat) + Refresh token (7 gun)
- **Rol Tabanli Erisim:** `@require_roles` dekoratoru ile `candidate`, `hr`, `admin` rolleri
- **Bootstrap Code:** HR ve Admin kaydi icin guvenlik kodu
- **Endpoint'ler:** `/auth/register`, `/auth/token`, `/auth/refresh`

### 4.2 CV Islem Hatti

1. Aday PDF CV yukler → `application_routes.py`
2. `CVParserAdapter` ile PDF metin cikarimi (pypdf)
3. Cok dilli beceri eslestirme (TR/EN alias destegi)
4. Regex tabanli deneyim yili tahmini (tarih araligi destegi)
5. Egitim seviyesi algilama (doktora → lise)
6. Kural tabanli skorlama: beceri %70 + deneyim %30
7. Skor >= 70 → Otomatik davet olusturma
8. Sonuclar veritabanina kaydedilir

### 4.3 Skorlama Stratejileri

| Strateji | Motor | Agirliklar | Benchmark F1 |
|----------|-------|------------|-------------|
| Rule-based (v1) | Kelime eslestirme | Skill %70, Exp %30 | 100% |
| Semantic (v2) | SBERT / TF-IDF fallback | Semantic %50, Skill %30, Exp %20 | 80% |

### 4.4 Raporlama

- **Ilan Bazli Rapor:** Basvuru sayisi, ortalama skor, davet durumu
- **Genel Bakis:** Toplam ilan, aday, basvuru, davet sayilari
- **Audit Log:** Tum HTTP isteklerinin IP, rol, method, path bilgisiyle kaydedilmesi

### 4.5 Onbellek (Cache)

- **Redis Cache Manager:** Singleton, TTL destegi, prefix invalidation
- **Cache Aside Pattern:** Ilan listesi ve raporlar onbelleklenir
- **Write-Through Invalidation:** Yeni ilan/basvuru olusturulunca ilgili cache temizlenir
- **In-Memory Fallback:** Redis yoksa bellek icinde onbellek

---

## 5. Test Sonuclari

### 5.1 Test Kapsami

| Kategori | Test Sayisi | Durum |
|----------|------------|-------|
| Saglık kontrolu | 1 | PASSED |
| Model testleri | 2 | PASSED |
| Match/skor testleri | 3 | PASSED |
| Auth/RBAC testleri | 7 | PASSED |
| CV upload testleri | 4 | PASSED |
| Kabul testleri (6 faz) | 23 | PASSED |
| **TOPLAM** | **40** | **40 PASSED** |

### 5.2 Skorlama Benchmark Sonuclari

```
Rule-based (v1):  Accuracy=100%  Precision=100%  Recall=100%  F1=100%
Semantic (v2):    Accuracy=83%   Precision=100%  Recall=67%   F1=80%
```

---

## 6. API Endpoint Ozeti

| Method | Endpoint | Rol | Aciklama |
|--------|----------|-----|----------|
| POST | `/api/v1/auth/register` | Public | Kullanici kaydi |
| POST | `/api/v1/auth/token` | Public | Token uretimi |
| POST | `/api/v1/auth/refresh` | Public | Token yenileme |
| POST | `/api/v1/candidates` | Public | Aday kaydi |
| GET | `/api/v1/jobs` | Auth | Ilan listesi |
| POST | `/api/v1/jobs` | HR/Admin | Ilan olusturma |
| POST | `/api/v1/applications/upload` | Candidate/Admin | CV yukleme |
| GET | `/api/v1/applications/me` | Candidate/Admin | Kendi basvurularim |
| POST | `/api/v1/match` | Public | Skor hesaplama |
| GET | `/api/v1/jobs/{id}/candidates` | HR/Admin | Aday listeleme |
| GET | `/api/v1/jobs/{id}/shortlisted` | HR/Admin | Kisa liste |
| GET | `/api/v1/invitations` | HR/Admin | Davet listesi |
| GET | `/api/v1/reports/jobs/{id}/summary` | HR/Admin | Ilan raporu |
| GET | `/api/v1/reports/overview` | HR/Admin | Genel bakis |
| GET | `/api/v1/audit-logs` | Admin | Audit kayitlari |
| GET | `/health` | Public | Saglik kontrolu |

---

## 7. Ekip ve Gorev Dagilimi

| Uye | Rol | Sorumluluklar | Tamamlanma |
|-----|-----|---------------|------------|
| Sitki Efe Kilinc | Proje Yoneticisi & Backend | Flask API, JWT Auth, RBAC, CV upload, audit log, final rapor | 9/9 |
| Zeynep Sutcu | AI/NLP Uzmani | PDF parse, kural/semantik skorlama, spaCy NLP, cok dilli destek | 8/8 |
| Ecem Nur Durak | Mobil/Frontend | Flutter uygulama, auth ekrani, rol dashboard, splash screen, tema | 9/10 |
| Samet Tanay | Veritabani Mimari | ORM, migration (Alembic), PostgreSQL, Redis, Docker | 8/8 |
| Serdar Korkmaz | Test & Dokumantasyon | 40 test, 8 dokuman, Postman, Docker prod | 10/10 |

---

## 8. Dizin Yapisi

```
Akilli-Ise-Alim-ve-Aday-Degerlendirme-Sistemi/
├── backend/
│   ├── app/
│   │   ├── core/              # Domain: Entities, Interfaces, ValueObjects, Enums
│   │   ├── application/       # CQRS: Commands, Queries, Services (Facade)
│   │   ├── infrastructure/    # DB, Cache, Scoring, Adapters, EventBus
│   │   └── presentation/      # API Routes, Middleware, WebSocket
│   ├── alembic/               # Veritabani migration dosyalari
│   ├── scripts/               # seed_data, scoring_benchmark
│   └── tests/                 # pytest test suite (40 test)
├── mobile_app/
│   └── lib/
│       ├── main.dart          # Flutter entry point
│       └── src/               # Models, Services, UI
├── docs/                      # Mimari, UML, Postman, UI/UX
├── docker-compose.yml         # Gelistirme ortami
├── docker-compose.prod.yml    # Uretim ortami
└── alembic.ini                # Alembic konfigurasyonu
```

---

## 9. Bilinen Kisitlamalar ve Gelecek Calismalari

### Bilinen Kisitlamalar
- spaCy ve sentence-transformers opsiyonel; yuklu degilse fallback kullanilir
- Flutter uygulaması fiziksel Android/iOS cihazda henuz test edilmedi
- Redis baglantisi yoksa in-memory fallback kullanilir

### Gelecek Calismalari
- spaCy Turkce model egitimi ile NER iyilestirmesi
- SBERT fine-tuning ile sektore ozel semantik skorlama
- Gercek zamanli bildirimler (WebSocket uzerinden)
- Kubernetes deployment manifesti
- CI/CD pipeline (GitHub Actions)

---

## 10. Sonuc

Proje, planlandigi gibi uçtan uca calisan bir ise alim platformu olarak tamamlanmistir. Onion Architecture ve 6 tasarim deseni ile modüler, test edilebilir ve genisletilebilir bir yapi olusturulmustur. 40 testin tamami basariyla gecmektedir.

Sistemin kural tabanli skorlama motoru %100 F1 skoru ile calisirken, semantik motor TF-IDF fallback modunda %80 F1 skoru uretmektedir. SBERT modeli yuklendiginde bu deger onemli olcude artacaktir.
