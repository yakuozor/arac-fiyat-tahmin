import pandas as pd
import numpy as np
import joblib
import os
import warnings

warnings.filterwarnings("ignore")

# =============================================================================
# KONFİGÜRASYON VE SABİTLER
# =============================================================================
MODEL_DOSYASI = "araba_fiyat_modeli.pkl"
OZEL_ARACLAR = ['s2000', 'supra', 'gt-r', 'type-r', 'm3', 'm4', 'm5', 'amg', '911', 'evo', 'wrx', 'cupra']

# Ekspertiz Değer Kayıp Oranları
DEGER_KAYBI = {
    'tavan_boya': 0.15,    
    'tavan_degisen': 0.20, 
    'kaput_boya': 0.04,    
    'kaput_degisen': 0.10, 
    'kapi_boya': 0.02,     
    'kapi_degisen': 0.04,  
    'bagaj_boya': 0.02,
    'bagaj_degisen': 0.05,
    'agir_hasar': 0.35     
}

VITES_CEVIRI = {'manuel': 'düz', 'otomatik': 'otomatik', 'yarı otomatik': 'yarı otomatik'}
YAKIT_CEVIRI = {'benzin': 'benzin', 'dizel': 'dizel', 'lpg': 'lpg & benzin', 'hibrit': 'hibrit'}

# =============================================================================
# MODEL YÜKLEME İŞLEMLERİ
# =============================================================================
if os.path.exists(MODEL_DOSYASI):
    print(f"Model yükleniyor: {MODEL_DOSYASI}")
    paket = joblib.load(MODEL_DOSYASI)
    model = paket["model"]
    le_marka = paket["le_marka"]
    le_seri = paket["le_seri"]
    le_model = paket["le_model"]
    le_vites = paket["le_vites"]
    le_yakit = paket["le_yakit"]
    df_ozel = paket["df_ozel"]
    df_ref = paket["df_ref"]
    print("Model ve ekspertiz modülü başarıyla başlatıldı.")
else:
    print(f"HATA: {MODEL_DOSYASI} bulunamadı. Lütfen önce modeli eğitin.")
    exit()

# =============================================================================
# FİYAT TAHMİN MOTORU
# =============================================================================
def fiyat_hesapla(marka, seri, yil, km, vites, yakit, 
                  paket_adi=None, 
                  boyalilar=None, 
                  degisenler=None, 
                  agir_hasar=False,
                  sunroof=False):
    """
    Verilen araç bilgilerine ve ekspertiz durumuna göre 2. el piyasa fiyatını tahmin eder.
    """
    
    if boyalilar is None: boyalilar = []
    if degisenler is None: degisenler = []

    # 1. Veri Ön İşleme
    marka, seri, vites, yakit = [x.lower().strip() for x in [marka, seri, vites, yakit]]
    vites_csv = VITES_CEVIRI.get(vites, vites)
    yakit_csv = YAKIT_CEVIRI.get(yakit, yakit)

    # 2. Özel / Koleksiyonluk Araç Kontrolü
    if any(x in seri for x in OZEL_ARACLAR):
        bulunanlar = df_ozel[df_ozel['seri'].str.contains(seri, na=False)]
        if len(bulunanlar) > 0:
            return f"\n[ÖZEL ARAÇ] {seri.upper()} -> Tahmini Fiyat Aralığı: {bulunanlar['fiyat'].min():,.0f} TL - {bulunanlar['fiyat'].max():,.0f} TL"

    try:
        # 3. Label Encoding ve Paket Tespiti
        m_kod = le_marka.transform([marka])[0]
        s_kod = le_seri.transform([seri])[0]
        v_kod = le_vites.transform([vites_csv])[0]
        y_kod = le_yakit.transform([yakit_csv])[0]
        
        ilgili_araclar = df_ref[
            (df_ref['seri'] == seri) & (df_ref['marka'] == marka) &
            (df_ref['vites_tipi'] == vites_csv) & (df_ref['yakit_tipi'] == yakit_csv)
        ]
        
        secilen_paket = ""
        if len(ilgili_araclar) == 0:
            ilgili_araclar = df_ref[(df_ref['seri'] == seri) & (df_ref['marka'] == marka)]
            secilen_paket = ilgili_araclar['model'].mode()[0] + " (Tahmini Paket)"
        elif paket_adi:
            uygun = ilgili_araclar[ilgili_araclar['model'].str.contains(paket_adi.lower(), na=False)]
            secilen_paket = uygun['model'].mode()[0] if len(uygun) > 0 else ilgili_araclar['model'].mode()[0]
        else:
            secilen_paket = ilgili_araclar['model'].mode()[0]

        mod_kod = le_model.transform([secilen_paket])[0]
        
        # 4. Model Tahmini (Hatasız Durum İçin)
        arac_yasi = 2026 - yil
        ham_fiyat = model.predict([[m_kod, s_kod, mod_kod, v_kod, y_kod, arac_yasi, km]])[0]
        
        # 5. Fiyat Optimizasyonu ve Ekspertiz Etkisi (Logic Layer)
        
        # A) Kilometre Sönümleme Regülasyonu
        if arac_yasi > 8 and km < 30000:
            tahmin_50k = model.predict([[m_kod, s_kod, mod_kod, v_kod, y_kod, arac_yasi, 50000]])[0]
            ham_fiyat = (ham_fiyat * 0.7) + (tahmin_50k * 0.3)

        # B) Hasar ve Değer Kaybı Hesaplaması
        toplam_indirim_orani = 0.0
        ekspertiz_notu = []
        
        if agir_hasar:
            toplam_indirim_orani += DEGER_KAYBI['agir_hasar']
            ekspertiz_notu.append("AĞIR HASAR KAYITLI")
        else:
            for parca in boyalilar:
                key = f"{parca}_boya"
                if key in DEGER_KAYBI:
                    toplam_indirim_orani += DEGER_KAYBI[key]
                    ekspertiz_notu.append(f"{parca.capitalize()} Boyalı (-%{DEGER_KAYBI[key]*100:.0f})")
            
            for parca in degisenler:
                key = f"{parca}_degisen"
                if key in DEGER_KAYBI:
                    toplam_indirim_orani += DEGER_KAYBI[key]
                    ekspertiz_notu.append(f"{parca.capitalize()} Değişen (-%{DEGER_KAYBI[key]*100:.0f})")

        toplam_indirim_orani = min(toplam_indirim_orani, 0.60) # Maksimum değer kaybı sınırı (%60)
        ekspertizli_fiyat = ham_fiyat * (1 - toplam_indirim_orani)

        # C) Ek Donanım Etkisi (Sunroof)
        if sunroof:
            if ekspertizli_fiyat > 1000000:
                ek_deger = ekspertizli_fiyat * 0.05
                ekspertizli_fiyat += ek_deger
                ekspertiz_notu.append(f"Sunroof Bonusu (+{ek_deger:,.0f} TL)")
            else:
                ekspertiz_notu.append("Sunroof Mevcut")

        # 6. Çıktı Raporlama
        print("-" * 60)
        print(f"Araç Bilgisi: {marka.upper()} {seri.upper()} ({yil})")
        print(f"Paket: {secilen_paket}")
        print(f"Detay: {km} km | {vites} | {yakit}")
        print(f"Ekspertiz: {', '.join(ekspertiz_notu) if ekspertiz_notu else 'Hatasız'}")
        print("-" * 60)
        print(f"Hatasız Piyasa Değeri  : {ham_fiyat:,.0f} TL")
        if toplam_indirim_orani > 0:
            print(f"Hasar Kaynaklı Düşüş   : -{(ham_fiyat - ekspertizli_fiyat):,.0f} TL")
        print(f"NET FİYAT TAHMİNİ      : {ekspertizli_fiyat:,.0f} TL")
        print("-" * 60)
        print()

    except Exception as e:
        print(f"Hesaplama Hatası: {e}")

# =============================================================================
# TEST SENARYOLARI
# =============================================================================
if __name__ == "__main__":
    fiyat_hesapla("Alfa Romeo", "Giulietta", 2016, 15000, "Manuel", "Dizel")
    
    fiyat_hesapla("Alfa Romeo", "Giulietta", 2016, 150000, "Manuel", "Dizel")
    
    fiyat_hesapla("Honda", "Civic", 2021, 50000, "Otomatik", "Benzin", 
                  boyalilar=['tavan', 'kapi'], sunroof=True)
    
    fiyat_hesapla("Fiat", "Egea", 2022, 40000, "Manuel", "Dizel", 
                  degisenler=['kaput'])
    
    fiyat_hesapla("Audi", "A3", 2016, 150000, "Otomatik", "Dizel")