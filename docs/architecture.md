# Mimari Taslak

## Mimari Stil
- Backend: Katmanli ve modul bazli yapi
- API: REST
- Veri: PostgreSQL + Redis

## Bilesenler
1. API Katmani
- Aday, ilan, eslestirme, admin endpointleri

2. Servis Katmani
- CV parsing servisi
- Skorlama servisi
- Mulakat/test tetikleme servisi

3. Veri Katmani
- Adaylar
- Ilanlar
- Basvurular
- Skor kayitlari
- Mulakat/test planlari
- Loglar

## Akis
1. Aday CV yukler
2. Parser oz nitelikleri cikarir
3. IK ilan olusturur
4. Skorlama modulu adaylari puanlar
5. IK panelinde sirali liste gorulur
6. Baraj ustu adaylara otomatik davet gider

## Tasarim Prensipleri
- Servisler arasi bagimliliklar gevsek tutulur
- NLP/skorlama adaptor yapisi ile degistirilebilir kurgulanir
- Dogrulama ve hata yonetimi API sinirinda merkezi yapilir
