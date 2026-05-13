# Akıllı İşe Alım — Flutter Mobil/Web Uygulaması

Multi-platform (Web, Windows, Android) Flutter uygulaması.  
Backend API ile iletişim kurarak aday yönetimi, ilan oluşturma ve raporlama işlevlerini sunar.

## Mimari

```
lib/
├── main.dart                  # Uygulama giriş noktası (Splash → App)
└── src/
    ├── models/
    │   └── session_state.dart  # Oturum durumu modeli
    ├── services/
    │   └── api_service.dart    # Backend REST API istemcisi
    └── ui/
        ├── theme.dart          # Merkezi tema sistemi (renk, tipografi)
        ├── splash_screen.dart  # Animasyonlu açılış ekranı
        └── app_shell.dart      # Auth + Dashboard ekranları
```

## Ekranlar

| Ekran | Rol | İçerik |
|-------|-----|--------|
| **Splash Screen** | Tümü | Animasyonlu logo, gradient arka plan |
| **Auth Screen** | Tümü | Kayıt & Giriş (rol seçimi, bootstrap code) |
| **Candidate Dashboard** | Candidate | Başvurularım, CV yükleme, ilan seçimi |
| **HR Dashboard** | HR | Yönetim özeti, ilan oluşturma, aday sıralaması, kısa liste |
| **Admin Dashboard** | Admin | HR + Audit kayıtları |

## Çalıştırma

```bash
cd mobile_app
flutter pub get
flutter run -d chrome      # Web
flutter run -d windows     # Windows
flutter run                # Android (cihaz bağlı ise)
```

## Bağımlılıklar

| Paket | Kullanım |
|-------|----------|
| `http` | REST API iletişimi |
| `file_picker` | CV PDF dosyası seçimi |

## Tema Sistemi

Merkezi tema `lib/src/ui/theme.dart` dosyasında tanımlıdır.  
Renk paleti, tipografi ve widget stilleri tek noktadan yönetilir.

## API Entegrasyonu

`ApiService` sınıfı tüm backend endpoint'lerini kapsar:
- `register()` — Kullanıcı kaydı
- `login()` — Token alımı
- `fetchJobs()` — İlan listesi
- `createJob()` — İlan oluşturma
- `uploadApplicationCv()` — CV yükleme
- `fetchJobCandidates()` — Aday listeleme
- `fetchShortlisted()` — Kısa liste
- `fetchInvitations()` — Davet listesi
- `fetchOverview()` — Genel bakış raporu
- `fetchAuditLogs()` — Audit kayıtları
- `fetchMyApplications()` — Adayın başvuruları
