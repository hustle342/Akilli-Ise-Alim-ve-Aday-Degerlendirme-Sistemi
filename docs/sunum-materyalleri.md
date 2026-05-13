# Sunum Materyalleri — Akilli Ise Alim ve Aday Degerlendirme Sistemi

**Ders:** Yazilim Tasarim ve Mimarisi  
**Tarih:** Mayis 2026  

---

## Slayt Icerigi

### Slayt 1 — Baslik
- **Proje:** Akilli Ise Alim ve Aday Degerlendirme Sistemi
- **Ekip:** Sitki Efe Kilinc, Zeynep Sutcu, Ecem Nur Durak, Samet Tanay, Serdar Korkmaz
- **Ders:** Yazilim Tasarim ve Mimarisi

### Slayt 2 — Problem Tanimi
- IK surecleri manuel ve zaman alici
- CV degerlendirme oznel ve tutarsiz
- Aday-ilan eslestirme sistematik degil
- **Cozum:** AI destekli otomatik CV analizi ve uyum skorlama

### Slayt 3 — Sistem Mimarisi
- Onion Architecture (Core → Application → Infrastructure → Presentation)
- 6 tasarim deseni: Singleton, Factory, Facade, Adapter, Strategy, Observer
- CQRS: Command/Query ayriligi
- ESB: Event-driven iletisim

### Slayt 4 — Teknoloji Yigini
| Katman | Teknoloji |
|--------|-----------|
| Backend | Flask 3.1.0 (Python) |
| Frontend | Flutter (Dart) — Web, Windows, Android |
| Veritabani | SQLite (dev) / PostgreSQL (prod) |
| Onbellek | Redis |
| Test | pytest (40 test) |
| NLP | spaCy, sentence-transformers |

### Slayt 5 — CV Islem Hatti
```
PDF Yukleme → Metin Cikarma → Beceri Eslestirme → Deneyim Tahmini
                                                      ↓
                           Skor Hesaplama (0-100) ← Kural Tabanli / Semantik
                                    ↓
                    Skor >= 70 → Otomatik Davet
```

### Slayt 6 — Skorlama Stratejileri
- **Kural Tabanli (v1):** Beceri %70 + Deneyim %30 → F1: 100%
- **Semantik (v2):** SBERT benzerlik %50 + Beceri %30 + Deneyim %20 → F1: 80%
- Strategy Pattern ile calisma zamaninda degistirilebilir

### Slayt 7 — Guvenlik
- JWT tabanli kimlik dogrulama (access + refresh token)
- Rol tabanli erisim kontrolu: `@require_roles(HR, ADMIN)`
- Audit log: Tum HTTP istekleri kaydedilir
- Bootstrap code ile admin/HR kaydi korumasi

### Slayt 8 — Flutter Istemci
- Multi-platform: Web, Windows, Android
- Rol tabanli dashboard: Candidate / HR / Admin
- Animasyonlu splash screen
- Material Design 3 tema sistemi

### Slayt 9 — Test Sonuclari
- 40 test: 17 birim + 23 kabul testi
- %100 gecme orani
- 6 benchmark senaryosu (tam uyum, kismi uyum, uyumsuz, asiri nitelikli, ...)
- Confusion matrix ile dogruluk olcumu

### Slayt 10 — Sonuc ve Degerler
- Modüler, test edilebilir, genisletilebilir mimari
- Production-ready: Docker, PostgreSQL, Redis
- Tüm ekip uyeleri sorumluluk alanlarını tamamlamistir
- Gelecek: SBERT fine-tuning, Kubernetes, CI/CD

---

## Demo Senaryosu

### Senaryo 1: Aday Kaydi ve CV Yukleme (2 dk)
1. Flutter uygulamasini ac (splash screen gosterimi)
2. "Kayit Ol" → Rol: Candidate → Kayit
3. Giris yap → Candidate Dashboard goruntule
4. Ilan sec → PDF CV yukle
5. Sonuc goster: Skor, parse edilmis bilgiler, davet durumu

### Senaryo 2: HR Ilan ve Aday Yonetimi (2 dk)
1. HR olarak giris yap
2. Yonetim Ozeti kartlarini goster (toplam ilan, aday, basvuru)
3. Yeni ilan olustur (baslik, yetenekler, deneyim)
4. Aday siralamasini goster (skorlar)
5. Kisa Liste kartini goster (baraj >= 70, davet durumlari)

### Senaryo 3: Admin Gozetimi (1 dk)
1. Admin olarak giris yap
2. Genel bakis raporunu goster
3. Audit log kayitlarini goster (method, path, IP, status)

### Senaryo 4: API Demo (1 dk)
1. Postman'da `/api/v1/match` endpoint'ini calistir
2. Aday profili ve ilan gereksinimleri gonder
3. Skor sonucunu ve nedenlerini goster
4. Skorlama stratejisini `semantic` olarak degistir ve farki goster

### Senaryo 5: Mimari Gosterim (1 dk)
1. Dizin yapisini goster (Core → Application → Infrastructure → Presentation)
2. `scoring_benchmark.py` ciktisini goster (precision, recall, F1)
3. Test suite'i calistir (40 PASSED)

---

## Soru-Cevap Hazirlik Notlari

**S: Neden Onion Architecture sectiniz?**
C: Bagimlilik yonunun iceriden disariya dogru olmasi sayesinde Core katmani hicbir dis kutuphanaye bagimli degil. Bu, test edilebilirlik ve genisletilebilirlik saglar.

**S: Semantik skorlama ne kadar dogruluklu?**
C: TF-IDF fallback modunda F1=%80. SBERT modeli yuklendiginde semantik benzerlik cok daha dogruluklu olur.

**S: Redis olmadan calisir mi?**
C: Evet. `RedisCacheManager` in-memory fallback kullaniyor. Redis yoksa bile sistem sorunsuz calisir.

**S: Neden itsdangerous yerine PyJWT kullanmadiniz?**
C: itsdangerous Flask ekosisteminin dogal parcasi ve SECRET_KEY uzerinden imzalama yaparak ayni guvenlik seviyesini saglar. Ek bagimlilik gerektirmez.

**S: Cok dilli CV destegi nasil calisiyor?**
C: CVParserAdapter Turkce ve Ingilizce anahtar kelimeleri algilar, Turkce alias'lari Ingilizce karsiliklarina cevirir (orn: "yapay zeka" → "machine learning").
