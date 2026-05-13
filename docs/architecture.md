# Mimari Doküman — Onion Architecture

## Katman Yapısı

```
┌─────────────────────────────────────────────────┐
│              PRESENTATION                       │
│  (API Routes, Middleware, WebSocket)             │
├─────────────────────────────────────────────────┤
│              APPLICATION                        │
│  (CQRS Commands/Queries, Facade, DTOs)          │
├─────────────────────────────────────────────────┤
│              INFRASTRUCTURE                     │
│  (DB, Adapters, Scoring, ESB, Notifications)    │
├─────────────────────────────────────────────────┤
│              CORE (DOMAIN)                      │
│  (Entities, Enums, Interfaces, Events, VOs)     │
└─────────────────────────────────────────────────┘
```

## Uygulanan Tasarım Kalıpları

### Creational (Yaratımsal)
- **Singleton**: `ConfigurationManager`, `DatabaseManager`, `InMemoryEventBus`
- **Factory Method**: `ScoringFactory` — farklı skorlama stratejileri üretir

### Structural (Yapısal)
- **Facade**: `RecruitmentFacade` — tüm alt servisleri tek arayüzden sunar
- **Adapter**: `CVParserAdapter` — PyPDF'i ICVParser'a adapt eder

### Behavioural (Davranışsal)
- **Strategy**: `IScoringStrategy` → `RuleBasedScoringStrategy`, `SemanticScoringStrategy`
- **Observer**: Event Handler'lar ESB üzerinden domain event'leri dinler

## OOP Prensipleri
- **Encapsulation**: DTO'lar, private alanlar
- **Inheritance**: `BaseEntity` → tüm entity'ler
- **Polymorphism**: Interface tabanlı repository/strategy değişimi
- **Abstraction**: `IRepository`, `IScoringStrategy`, `ICVParser`, `IEventBus`

## CQRS
- Commands: `RegisterUserCommand`, `CreateJobCommand`, `UploadCVCommand`
- Queries: `GetJobsQuery`, `GetMyApplicationsQuery`, `GetJobCandidatesQuery`, `GetReportQuery`

## ESB
- `InMemoryEventBus` — Redis Pub/Sub için hazır arayüz
- Olaylar: `application.created`, `score.calculated`, `invitation.sent`, `user.registered`, `job.created`

## Real-Time
- WebSocket desteği `flask-socketio` ile (opsiyonel bağımlılık)
