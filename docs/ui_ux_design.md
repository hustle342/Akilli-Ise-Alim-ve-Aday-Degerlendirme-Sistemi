# UI/UX Tasarım Rehberi — Akıllı İşe Alım ve Aday Değerlendirme Sistemi

## 1. Renk Paleti

| Renk           | Kod       | Kullanım                    |
|----------------|-----------|-----------------------------|
| Primary Dark   | `#0A2540` | AppBar, Splash arka plan    |
| Primary        | `#0E5A8A` | Butonlar, ikonlar, vurgular |
| Primary Light  | `#3A8CC2` | Hover durumları             |
| Accent         | `#F5A623` | Önemli uyarılar, badge      |
| Accent Light   | `#F6E6C5` | Auth gradient son renk      |
| Background     | `#F4F1E8` | Scaffold arka plan          |
| Surface        | `#FFFFFF` | Card arka plan              |
| Surface Alt    | `#F4F8FB` | Alternatif card arka plan   |
| Text Primary   | `#102A43` | Başlık ve ana metin         |
| Text Secondary | `#627D98` | Alt metin, açıklama         |
| Success        | `#166534` | Başarı mesajları            |
| Error          | `#991B1B` | Hata mesajları              |

## 2. Tipografi

| Stil            | Boyut | Ağırlık   | Kullanım           |
|-----------------|-------|-----------|---------------------|
| Headline Medium | 28px  | Bold (700)| Sayfa başlıkları   |
| Title Large     | 22px  | Semi (600)| Bölüm başlıkları   |
| Title Medium    | 16px  | Medium    | Card başlıkları    |
| Body Medium     | 14px  | Regular   | Ana metin          |
| Body Small      | 12px  | Regular   | Alt metin          |

## 3. Bileşen Tasarımı

### Card
- Border Radius: 24px
- Elevation: 0 (flat design)
- Padding: 20px

### Butonlar
- FilledButton: 18px border radius, primary renk
- OutlinedButton: 18px border radius, primary outline
- TextButton: Düz metin stil

### Input Alanları
- Border Radius: 18px
- OutlinedBorder stili
- Content padding: 16px horizontal, 14px vertical

## 4. Ekran Akışı

```
Splash Screen (2.5s)
    ├── [Giriş Yok] → Auth Screen
    │       ├── Login Tab
    │       └── Register Tab (rol seçimi, bootstrap code)
    └── [Giriş Var] → Dashboard
            ├── [Candidate Rol] → Başvurularım + CV Yükleme
            ├── [HR Rol] → Yönetim Özeti + İlan Yönetimi + Aday Sıralaması + Kısa Liste
            └── [Admin Rol] → Yönetim Özeti + İlan Yönetimi + Kısa Liste + Audit Kayıtları
```

## 5. Responsive Tasarım

- Max width constraint: 520px (Auth ekranı)
- Card grid: Wrap layout (180px per card)
- ListView: 20px padding

## 6. Animasyonlar

- Splash: FadeIn + ScaleUp (1.8s, easeOutBack)
- Loading: CircularProgressIndicator
- Sayfa geçişleri: MaterialApp default transitions

## 7. Platform Desteği

| Platform | Durum |
|----------|-------|
| Web      | ✅    |
| Windows  | ✅    |
| Android  | ✅    |
