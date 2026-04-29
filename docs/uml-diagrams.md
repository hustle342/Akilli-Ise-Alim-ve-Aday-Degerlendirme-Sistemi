# UML Diyagramlari

Bu dosya Mermaid sözdizimi ile hazırlanmış Class, Use Case ve Sequence diyagramlarını içerir.

---

## 1. Sinif Diyagrami (Class Diagram)

```mermaid
classDiagram
    class User {
        +int id
        +str full_name
        +str email
        +str password_hash
        +UserRole role
        +datetime created_at
    }

    class JobPosting {
        +int id
        +str title
        +str description
        +int min_years_experience
        +str required_skills
        +datetime created_at
    }

    class Application {
        +int id
        +int candidate_id
        +int job_posting_id
        +str cv_path
        +str parsed_summary
        +ApplicationStatus status
        +datetime created_at
    }

    class MatchScore {
        +int id
        +int application_id
        +float score
        +str rationale
        +str scoring_version
        +datetime created_at
    }

    class Invitation {
        +int id
        +int application_id
        +InvitationType invitation_type
        +InvitationStatus status
        +datetime scheduled_at
        +datetime created_at
    }

    class AuditLog {
        +int id
        +str method
        +str path
        +int status_code
        +str ip_address
        +str actor_type
        +int user_id
        +str role
        +datetime created_at
    }

    class CVParserService {
        +parse_bytes(bytes) dict
        +save_cv(bytes, filename) str
    }

    class ScoringService {
        +calculate(candidate, job) tuple
    }

    class UserRole {
        <<enumeration>>
        CANDIDATE
        HR
        ADMIN
    }

    class ApplicationStatus {
        <<enumeration>>
        APPLIED
        SHORTLISTED
        REJECTED
        HIRED
    }

    class InvitationType {
        <<enumeration>>
        TEST
        INTERVIEW
    }

    class InvitationStatus {
        <<enumeration>>
        PENDING
        SENT
        COMPLETED
        CANCELED
    }

    User "1" --> "0..*" Application : yapar
    JobPosting "1" --> "0..*" Application : alir
    Application "1" --> "1" MatchScore : üretir
    Application "1" --> "0..*" Invitation : tetikler
    User --> UserRole
    Application --> ApplicationStatus
    Invitation --> InvitationType
    Invitation --> InvitationStatus
    CVParserService ..> Application : parse
    ScoringService ..> MatchScore : hesaplar
```

---

## 2. Kullanim Durumu Diyagrami (Use Case Diagram)

```mermaid
graph LR
    Candidate((Aday))
    HR((IK Uzmani))
    Admin((Admin))
    System[Akilli Ise Alim Sistemi]

    Candidate -->|Kayit ol| UC1[Kullanici Kaydi]
    Candidate -->|Giris yap| UC2[Token Al]
    Candidate -->|PDF CV yukle| UC3[CV Yukleme ve Parse]
    Candidate -->|Basvurularimi gor| UC4[Basvuru Listeleme]

    HR -->|Giris yap| UC2
    HR -->|Ilan olustur| UC5[Ilan Yonetimi]
    HR -->|Aday listele| UC6[Aday Siralamasi]
    HR -->|Kisa listeyi gor| UC7[Kisa Liste Goruntuleme]
    HR -->|Davetleri gor| UC8[Davet Takibi]
    HR -->|Rapor al| UC9[Raporlama]

    Admin -->|Giris yap| UC2
    Admin -->|HR yetkisi ver| UC1
    Admin -->|Audit loglari gor| UC10[Audit Log Goruntuleme]
    Admin -->|Tum IK islemleri| UC5
    Admin -->|Tum IK islemleri| UC6
    Admin -->|Tum IK islemleri| UC7
    Admin -->|Tum IK islemleri| UC9

    UC3 --> UC11[Skor Hesaplama]
    UC11 --> UC12[Otomatik Davet]
```

---

## 3. Sıra Diyagrami — CV Yukleme ve Otomatik Davet Akisi (Sequence Diagram)

```mermaid
sequenceDiagram
    actor Aday
    participant Flutter as Flutter Istemci
    participant API as Flask API
    participant CVParser as CV Parser
    participant Scorer as Scoring Service
    participant DB as Veritabani

    Aday->>Flutter: PDF dosyasini sec ve Yukle'ye bas
    Flutter->>API: POST /api/v1/applications/upload\n(Bearer token, cv_file, candidate_id, job_posting_id)
    API->>API: Token dogrula (require_roles: candidate/admin)
    API->>CVParser: parse_bytes(pdf_bytes)
    CVParser-->>API: {summary, skills, years_experience}
    API->>DB: Application kaydini olustur
    API->>DB: JobPosting'i getir
    API->>Scorer: calculate(candidate_proxy, job_proxy)
    Scorer-->>API: (score, reasons)
    API->>DB: MatchScore kaydini olustur
    alt score >= threshold (70)
        API->>DB: Invitation (SENT) kaydini olustur
        API->>DB: Application.status = SHORTLISTED
    end
    API-->>Flutter: {application_id, score, status, invitation?}
    Flutter-->>Aday: Yukleme sonucu goster
```

---

## 4. Sıra Diyagrami — HR Kisa Liste Goruntuleme (Sequence Diagram)

```mermaid
sequenceDiagram
    actor HR as IK Uzmani
    participant Flutter as Flutter Istemci
    participant API as Flask API
    participant DB as Veritabani

    HR->>Flutter: Ilan sec
    Flutter->>API: GET /api/v1/jobs/{id}/shortlisted?threshold=70\n(Bearer token)
    API->>API: Token dogrula (require_roles: hr/admin)
    API->>DB: Application + User + MatchScore JOIN\nfilter score >= 70
    DB-->>API: Kayitlar
    API-->>Flutter: {candidates: [{application_id, candidate_name, score}]}

    Flutter->>API: GET /api/v1/invitations?job_posting_id={id}\n(Bearer token)
    API->>DB: Invitation + Application + User JOIN\nfilter job_posting_id
    DB-->>API: Davet kayitlari
    API-->>Flutter: {invitations: [{application_id, type, status, ...}]}

    Flutter-->>HR: Kisa liste kartlarini goster\n(Skor + Davet durumu)
```
