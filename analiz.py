import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'DejaVu Sans'

plt.style.use('ggplot')

pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)
pd.set_option('display.max_rows',100)

print("="*60)
print("✅ Kütüphaneler başarıyla yüklendi!")
print(f"✅ Pandas versiyonu: {pd.__version__}")
print(f"✅ NumPy versiyonu: {np.__version__}")
print("="*60)

# ============================================================
# BÖLÜM 1: VERİ YÜKLEME VE İLK İNCELEME
# ============================================================

print("\n" + "="*60)
print("📂 VERİ YÜKLEME")
print("="*60)

# Veriyi yükle
try:
    df_basket = pd.read_csv('basket_details.csv', encoding='utf-8')
    df_customer = pd.read_csv('customer_details.csv', encoding='utf-8')
    print(f"✅ Veri başarıyla yüklendi!")
    print(f"📊 Toplam Satır: {len(df_basket):,}")
    print(f"📊 Toplam Kolon: {len(df_basket.columns)}")
    print(f"📊 Toplam Satır: {len(df_customer):,}")
    print(f"📊 Toplam Kolon: {len(df_customer.columns)}")
    # df_customer'ı yükledikten hemen sonra bu satırı ekleyin:
    print("\n" + "="*60)
    print("🔍 'sex' SÜTUNU KONTROLÜ (TEMİZLİK ÖNCESİ)")
    print("="*60)
    # Bu satır, o sütundaki tüm benzersiz (unique) değerleri size listeler
    print(f"Benzersiz değerler: {df_customer['sex'].unique()}")
    replace_map = {
        'kvkktalepsilindi': 'Diğer',
        'UNKNOWN': 'Diğer'
        # NOT: Eğer ' male ' (boşluklu) veya 'female' (küçük harf) gibi
        # sorunlar da olsaydı, önceki adımdaki .str.strip().str.title()
        # kodunu da buraya eklememiz gerekirdi. Şimdilik buna odaklanalım.
    }

    df_customer['sex'] = df_customer['sex'].replace(replace_map)
    print(f"Benzersiz değerler: {df_customer['sex'].unique()}")

except FileNotFoundError:
    print("❌ HATA: Veri dosyası bulunamadı!")
    print("📁 Lütfen 'basket_details.csv' veya 'customer_details.csv' dosyasının")
    print("   aynı klasörde olduğundan emin ol.")
    exit()
except Exception as e:
    print(f"❌ HATA: {e}")
    exit()

# İlk 5 satıra bak
print("\n" + "="*60)
print("👀 İLK 5 SATIR")
print("="*60)
print(df_customer.head())

# Kolon isimlerini göster
print("\n" + "="*60)
print("📋 KOLONLAR")
print("="*60)
for i, col in enumerate(df_customer.columns, 1):
    print(f"{i}. {col}")

# Veri tipleri
print("\n" + "="*60)
print("🔍 VERİ TİPLERİ")
print("="*60)
print(df_customer.dtypes)

# Temel istatistikler
print("\n" + "="*60)
print("📈 TEMEL İSTATİSTİKLER")
print("="*60)
print(df_customer.describe())

print("\n" + "="*60)
print("🔍 KEŞİFSEL VERİ ANALİZİ")
print("="*60)

print("\n📋 Mevcut Kolonlar:")
print(df_customer.columns.tolist())

df_merge = pd.merge(df_basket,df_customer,on='customer_id',how="left")
print("\n📋 Mevcut Kolonlar:")
print(df_merge.columns.tolist())
print(f"📊 Toplam Satır: {len(df_merge):,}")
print(f"📊 Toplam Kolon: {len(df_merge.columns)}")

if 'product_id' in df_merge.columns and 'basket_count' in df_merge.columns:
    print("\n" + "="*60)
    print("🏆 EN ÇOK SATAN 10 ÜRÜN")
    print("="*60)
    urun_satislari = df_merge.groupby('product_id')['basket_count'].sum()
    top10 = urun_satislari.sort_values(ascending=False).head(10)
    print(top10)
    top10_product_ids = top10.index.tolist()
    df_top10_sales = df_merge[df_merge['product_id'].isin(top10_product_ids)]
    gender_sales = df_top10_sales.groupby(['product_id','sex'])['basket_count'].sum()
    gender_sales_pivot = gender_sales.unstack(level='sex').fillna(0)
    gender_sales_pivot = gender_sales_pivot.reindex(top10_product_ids)

    print("cinsiyet")

    print(gender_sales_pivot)
else:
    print("\n⚠️ 'Product' veya 'Quantity' kolonu bulunamadı!")
    print("Lütfen kolon isimlerini kontrol et.")
    
# if 'sex' in df_customer.columns and 'customer_id' in df_customer.columns and 'customer_id' in df_basket.columns:
    