# Gereksinim Dokumani

## Problem Tanimi
IK ekipleri yuksek basvuru hacmi nedeniyle manuel elemede zaman, kalite ve tutarlilik kaybi yasamaktadir.

## Amac
Dogru pozisyona dogru adayi daha hizli ve objektif sekilde eslestirmek.

## Kapsam
- Aday kaydi ve CV yukleme
- CV metin cikarma ve yetkinlik ayrisimi
- Ilan kriter tanimlama
- Aday-ilan eslestirme ve uyum skoru
- Baraj ustu adaylar icin test/mulakat atama
- Surec loglama ve yetkilendirme

## Fonksiyonel Gereksinimler
1. Aday sisteme kayit olabilmelidir.
2. Aday PDF formatinda CV yukleyebilmelidir.
3. Sistem CV'den temel nitelikleri cikarmalidir.
4. IK uzmani ilan olusturabilmeli ve filtreleri girebilmelidir.
5. Sistem uyum skoru hesaplayip sirali aday listesi donmelidir.
6. Sistem baraj puanina gore otomatik davet sureci baslatabilmelidir.
7. Admin rolunde log ve yetki yonetimi bulunmalidir.

## Fonksiyonel Olmayan Gereksinimler
- Performans: Ilan bazli skorlama islemi kabul edilebilir surede tamamlanmali
- Guvenlik: Rol tabanli erisim, temel veri dogrulama, loglama
- Surdurulebilirlik: Katmanli mimari, test edilebilir servis tasarimi
- Genisletilebilirlik: NLP/model katmani degistirilebilir olmali

## Basari Kriterleri
- Manuel eleme suresinde ciddi azalis
- Ust siradaki adaylarda yuksek teknik mulakat gecis orani
- Adaylara hizli geri bildirim surecinin isletilmesi
