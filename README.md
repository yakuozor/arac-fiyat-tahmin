# 🚗 2. El Araç Fiyat Tahmin ve Ekspertiz Motoru

Bu proje, Türkiye'deki 2. el otomobil piyasası verilerini kullanarak araçların güncel piyasa değerini tahmin eden gelişmiş bir makine öğrenmesi projesidir. Standart tahmin modellerinden farklı olarak, projenin içerisinde gerçek dünya dinamiklerini simüle eden bir **Logic Layer (Mantık Katmanı)** bulunmaktadır.

## 🌟 Öne Çıkan Özellikler

* **Makine Öğrenmesi ile Hatasız Fiyat Tahmini:** Araç marka, model, yıl, km, vites ve yakıt tipine göre taban fiyat tahmini.
* **Gelişmiş Ekspertiz Modülü (Logic Layer):** Aracın boyalı/değişen parçalarına ve ağır hasar kayıt durumuna göre dinamik değer kaybı hesaplaması (Maksimum %60'a kadar sınırlandırılmış sönümleme).
* **Özel/Koleksiyon Araç Filtresi:** S2000, Supra, M3, 911 gibi özel araçlar için standart model yerine spesifik fiyat aralığı analizi.
* **Kilometre ve Yaş Sönümlemesi:** Yaşlı ama düşük kilometreli araçlarda modelin aşırı fiyat vermesini engelleyen, gerçekçi fiyat frenleme sistemi.
* **Donanım Çarpanı:** Belirli bir fiyatın (1 Milyon TL) üzerindeki araçlarda Sunroof gibi premium donanımların fiyata olan yüzdesel (+%5) etkisi.

## 🛠️ Kullanılan Teknolojiler

* **Dil:** Python 3.x
* **Veri İşleme:** Pandas, NumPy
* **Makine Öğrenmesi:** Scikit-learn
* **Model Kayıt/Yükleme:** Joblib

## 🚀 Kurulum ve Kullanım

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1. **Repoyu klonlayın:**
   ```bash
   git clone [https://github.com/yakuozor/arac-fiyat-tahmin.git](https://github.com/yakuozor/arac-fiyat-tahmin.git)
   cd arac-fiyat-tahmin


2.  Model Dosyasını İndirin (Önemli!):
GitHub'ın 100 MB dosya boyutu sınırı nedeniyle, 195 MB'lık eğitilmiş yapay zeka modeli (araba_fiyat_modeli.pkl) repoya dahil edilmemiştir. Kodu çalıştırmadan önce modeli aşağıdaki bağlantıdan indirip projenin ana klasörünün içine kopyalamanız gerekmektedir:

https://drive.google.com/file/d/1EPQGlWQ5jJ2izxKVOW4stK47GMdCf-dW/view

3. Gerekli Kütüphaneler İndirin:
pip install pandas numpy scikit-learn joblib

4. Tahmin motorunu çalıştırın:
python main.py