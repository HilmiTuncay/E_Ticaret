import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
import sys
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# ============================================================
# MATPLOTLIB AYARLARI
# ============================================================
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

# ============================================================
# PANDAS AYARLARI
# ============================================================
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

print("="*80)
print("🛒 E-TİCARET SATIŞ ANALİZ RAPORU")
print("="*80)
print(f"✅ Pandas versiyonu: {pd.__version__}")
print(f"✅ NumPy versiyonu: {np.__version__}")
print("="*80)

# ============================================================
# AŞAMA 1: VERİ YÜKLEME VE HAZIRLIK
# ============================================================

print("\n" + "="*80)
print("📂 AŞAMA 1: VERİ YÜKLEME VE HAZIRLIK")
print("="*80)

try:
    # Veri yükleme
    df_basket = pd.read_csv('basket_details.csv', encoding='utf-8')
    df_customer = pd.read_csv('customer_details.csv', encoding='utf-8')

    print(f"✅ Veriler başarıyla yüklendi!")
    print(f"\n📊 Sepet Detayları:")
    print(f"   - Toplam Satır: {len(df_basket):,}")
    print(f"   - Toplam Kolon: {len(df_basket.columns)}")
    print(f"   - Kolonlar: {', '.join(df_basket.columns)}")

    print(f"\n📊 Müşteri Detayları:")
    print(f"   - Toplam Satır: {len(df_customer):,}")
    print(f"   - Toplam Kolon: {len(df_customer.columns)}")
    print(f"   - Kolonlar: {', '.join(df_customer.columns)}")

except FileNotFoundError:
    print("❌ HATA: Veri dosyası bulunamadı!")
    print("📁 Lütfen 'basket_details.csv' ve 'customer_details.csv' dosyalarının")
    print("   aynı klasörde olduğundan emin olun.")
    exit()
except Exception as e:
    print(f"❌ HATA: {e}")
    exit()

# Veri temizleme ve hazırlık
print("\n🧹 Veri Temizleme:")

# Tarih kolonunu datetime'a çevir
df_basket['basket_date'] = pd.to_datetime(df_basket['basket_date'])
print("   ✓ Tarih kolonu datetime formatına çevrildi")

# Müşteri verisindeki sex kolonunu temizle
replace_map = {
    'kvkktalepsilindi': 'Diğer',
    'UNKNOWN': 'Diğer'
}
df_customer['sex'] = df_customer['sex'].replace(replace_map)
print("   ✓ Cinsiyet kolonu temizlendi")

# Yaş anomalilerini düzelt (124 yaş gibi)
df_customer.loc[df_customer['customer_age'] > 100, 'customer_age'] = df_customer['customer_age'].median()
print("   ✓ Yaş anomalileri düzeltildi")

# Birleştirme
df_merge = pd.merge(df_basket, df_customer, on='customer_id', how='left')
print(f"\n✅ Veriler birleştirildi!")
print(f"   - Toplam Satır: {len(df_merge):,}")
print(f"   - Toplam Kolon: {len(df_merge.columns)}")

# Eksik veri kontrolü
print(f"\n❓ Eksik Veri Kontrolü:")
missing = df_merge.isnull().sum()
if missing.sum() > 0:
    print(missing[missing > 0])
else:
    print("   ✓ Eksik veri bulunmamaktadır")

# Zaman bazlı özellikler ekle
df_merge['year'] = df_merge['basket_date'].dt.year
df_merge['month'] = df_merge['basket_date'].dt.month
df_merge['day_of_week'] = df_merge['basket_date'].dt.day_name()
df_merge['week'] = df_merge['basket_date'].dt.isocalendar().week

# Yaş grupları oluştur
df_merge['age_group'] = pd.cut(df_merge['customer_age'],
                                bins=[0, 25, 35, 45, 55, 100],
                                labels=['18-25', '26-35', '36-45', '46-55', '55+'])

print("   ✓ Zaman ve yaş grup özellikleri eklendi")

# ============================================================
# AŞAMA 2: KEŞİFSEL VERİ ANALİZİ (EDA)
# ============================================================

print("\n" + "="*80)
print("🔍 AŞAMA 2: KEŞİFSEL VERİ ANALİZİ (EDA)")
print("="*80)

# Temel istatistikler
print("\n📈 TEMEL İSTATİSTİKLER:")
print(f"   - Toplam Satış Adedi: {df_merge['basket_count'].sum():,.0f}")
print(f"   - Toplam Eşsiz Müşteri: {df_merge['customer_id'].nunique():,}")
print(f"   - Toplam Eşsiz Ürün: {df_merge['product_id'].nunique():,}")
print(f"   - Ortalama Sepet Büyüklüğü: {df_merge['basket_count'].mean():.2f}")
print(f"   - Medyan Sepet Büyüklüğü: {df_merge['basket_count'].median():.2f}")
print(f"   - Tarih Aralığı: {df_merge['basket_date'].min().date()} - {df_merge['basket_date'].max().date()}")

# 1. EN ÇOK SATAN ÜRÜNLER
print("\n" + "-"*80)
print("🏆 EN ÇOK SATAN 10 ÜRÜN")
print("-"*80)
top_products = df_merge.groupby('product_id')['basket_count'].agg(['sum', 'count']).sort_values('sum', ascending=False).head(10)
top_products.columns = ['Toplam Satış', 'Sipariş Sayısı']
print(top_products)

# 2. CİNSİYET BAZLI SATIŞ ANALİZİ
print("\n" + "-"*80)
print("👥 CİNSİYET BAZLI SATIŞ ANALİZİ")
print("-"*80)
gender_sales = df_merge.groupby('sex')['basket_count'].agg(['sum', 'mean', 'count'])
gender_sales.columns = ['Toplam Satış', 'Ortalama Sepet', 'Sipariş Sayısı']
gender_sales['Yüzde'] = (gender_sales['Toplam Satış'] / gender_sales['Toplam Satış'].sum() * 100).round(2)
print(gender_sales)

# 3. YAŞ GRUBU BAZLI SATIŞ ANALİZİ
print("\n" + "-"*80)
print("📊 YAŞ GRUBU BAZLI SATIŞ ANALİZİ")
print("-"*80)
age_sales = df_merge.groupby('age_group')['basket_count'].agg(['sum', 'mean', 'count']).sort_values('sum', ascending=False)
age_sales.columns = ['Toplam Satış', 'Ortalama Sepet', 'Sipariş Sayısı']
age_sales['Yüzde'] = (age_sales['Toplam Satış'] / age_sales['Toplam Satış'].sum() * 100).round(2)
print(age_sales)

# 4. ZAMAN BAZLI SATIŞ TRENDİ
print("\n" + "-"*80)
print("📅 GÜNLÜK SATIŞ TRENDİ")
print("-"*80)
daily_sales = df_merge.groupby('basket_date')['basket_count'].sum().sort_index()
print(f"   - En yüksek satış günü: {daily_sales.idxmax().date()} ({daily_sales.max():,.0f} adet)")
print(f"   - En düşük satış günü: {daily_sales.idxmin().date()} ({daily_sales.min():,.0f} adet)")
print(f"   - Günlük ortalama satış: {daily_sales.mean():.0f} adet")

# 5. HAFTANIN GÜNÜ ANALİZİ
print("\n" + "-"*80)
print("📆 HAFTANIN GÜNÜ ANALİZİ")
print("-"*80)
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_sales = df_merge.groupby('day_of_week')['basket_count'].agg(['sum', 'mean', 'count'])
day_sales = day_sales.reindex(day_order)
day_sales.columns = ['Toplam Satış', 'Ortalama Sepet', 'Sipariş Sayısı']
day_sales.index = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
print(day_sales)

# 6. MÜŞTERİ SADAKATİ ANALİZİ (TENURE)
print("\n" + "-"*80)
print("💎 MÜŞTERİ SADAKATİ ANALİZİ (TENURE)")
print("-"*80)
tenure_groups = pd.cut(df_merge['tenure'], bins=[0, 60, 90, 120, 150], labels=['Yeni (0-60)', 'Orta (61-90)', 'Sadık (91-120)', 'Çok Sadık (120+)'])
tenure_sales = df_merge.groupby(tenure_groups)['basket_count'].agg(['sum', 'mean', 'count'])
tenure_sales.columns = ['Toplam Satış', 'Ortalama Sepet', 'Sipariş Sayısı']
tenure_sales['Yüzde'] = (tenure_sales['Toplam Satış'] / tenure_sales['Toplam Satış'].sum() * 100).round(2)
print(tenure_sales)

# ============================================================
# AŞAMA 3: VERİ GÖRSELLEŞTİRME (MATPLOTLIB)
# ============================================================

print("\n" + "="*80)
print("📊 AŞAMA 3: VERİ GÖRSELLEŞTİRME")
print("="*80)

# Grafik 1: En Çok Satan 10 Ürün
fig, ax = plt.subplots(figsize=(12, 6))
top_products_plot = df_merge.groupby('product_id')['basket_count'].sum().sort_values(ascending=False).head(10)
bars = ax.barh(range(len(top_products_plot)), top_products_plot.values, color='#3498db')
ax.set_yticks(range(len(top_products_plot)))
ax.set_yticklabels([f'Ürün {pid}' for pid in top_products_plot.index])
ax.set_xlabel('Toplam Satış Adedi', fontsize=12, fontweight='bold')
ax.set_title('En Çok Satan 10 Ürün', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
# Değerleri çubukların üzerine yaz
for i, bar in enumerate(bars):
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2, f'{int(width):,}',
            ha='left', va='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('grafik_1_top_urunler.png', dpi=300, bbox_inches='tight')
print("   ✓ Grafik 1: En Çok Satan 10 Ürün kaydedildi (grafik_1_top_urunler.png)")
plt.close()

# Grafik 2: Cinsiyet Bazlı Satış Dağılımı
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Pasta grafiği
gender_total = df_merge.groupby('sex')['basket_count'].sum()
colors = ['#3498db', '#e74c3c', '#95a5a6']
wedges, texts, autotexts = ax1.pie(gender_total.values, labels=gender_total.index, autopct='%1.1f%%',
                                     colors=colors, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax1.set_title('Cinsiyet Bazlı Satış Dağılımı', fontsize=14, fontweight='bold', pad=20)

# Bar grafiği
gender_sales_plot = df_merge.groupby('sex')['basket_count'].sum().sort_values(ascending=False)
bars = ax2.bar(gender_sales_plot.index, gender_sales_plot.values, color=colors)
ax2.set_xlabel('Cinsiyet', fontsize=12, fontweight='bold')
ax2.set_ylabel('Toplam Satış Adedi', fontsize=12, fontweight='bold')
ax2.set_title('Cinsiyet Bazlı Toplam Satışlar', fontsize=14, fontweight='bold', pad=20)
# Değerleri çubukların üzerine yaz
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('grafik_2_cinsiyet_analizi.png', dpi=300, bbox_inches='tight')
print("   ✓ Grafik 2: Cinsiyet Bazlı Satış Dağılımı kaydedildi (grafik_2_cinsiyet_analizi.png)")
plt.close()

# Grafik 3: Yaş Grubu Bazlı Satış Analizi
fig, ax = plt.subplots(figsize=(12, 6))
age_sales_plot = df_merge.groupby('age_group')['basket_count'].sum().sort_values(ascending=False)
bars = ax.bar(age_sales_plot.index.astype(str), age_sales_plot.values, color='#2ecc71')
ax.set_xlabel('Yaş Grubu', fontsize=12, fontweight='bold')
ax.set_ylabel('Toplam Satış Adedi', fontsize=12, fontweight='bold')
ax.set_title('Yaş Grubu Bazlı Satış Analizi', fontsize=14, fontweight='bold', pad=20)
# Değerleri çubukların üzerine yaz
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('grafik_3_yas_grubu_analizi.png', dpi=300, bbox_inches='tight')
print("   ✓ Grafik 3: Yaş Grubu Bazlı Satış Analizi kaydedildi (grafik_3_yas_grubu_analizi.png)")
plt.close()

# Grafik 4: Günlük Satış Trendi
fig, ax = plt.subplots(figsize=(14, 6))
daily_sales_plot = df_merge.groupby('basket_date')['basket_count'].sum()
ax.plot(daily_sales_plot.index, daily_sales_plot.values, linewidth=2, color='#9b59b6', marker='o', markersize=4)
ax.fill_between(daily_sales_plot.index, daily_sales_plot.values, alpha=0.3, color='#9b59b6')
ax.set_xlabel('Tarih', fontsize=12, fontweight='bold')
ax.set_ylabel('Toplam Satış Adedi', fontsize=12, fontweight='bold')
ax.set_title('Günlük Satış Trendi', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('grafik_4_gunluk_satis_trendi.png', dpi=300, bbox_inches='tight')
print("   ✓ Grafik 4: Günlük Satış Trendi kaydedildi (grafik_4_gunluk_satis_trendi.png)")
plt.close()

# Grafik 5: Haftanın Günü Satış Analizi
fig, ax = plt.subplots(figsize=(12, 6))
day_order_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_labels_tr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
day_sales_plot = df_merge.groupby('day_of_week')['basket_count'].sum().reindex(day_order_en)
bars = ax.bar(day_labels_tr, day_sales_plot.values, color='#e67e22')
ax.set_xlabel('Haftanın Günü', fontsize=12, fontweight='bold')
ax.set_ylabel('Toplam Satış Adedi', fontsize=12, fontweight='bold')
ax.set_title('Haftanın Günü Bazlı Satış Analizi', fontsize=14, fontweight='bold', pad=20)
# Değerleri çubukların üzerine yaz
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('grafik_5_haftanin_gunu_analizi.png', dpi=300, bbox_inches='tight')
print("   ✓ Grafik 5: Haftanın Günü Bazlı Satış Analizi kaydedildi (grafik_5_haftanin_gunu_analizi.png)")
plt.close()

# Grafik 6: Müşteri Sadakati (Tenure) Analizi
fig, ax = plt.subplots(figsize=(12, 6))
tenure_groups_plot = pd.cut(df_merge['tenure'], bins=[0, 60, 90, 120, 150], labels=['Yeni\n(0-60)', 'Orta\n(61-90)', 'Sadık\n(91-120)', 'Çok Sadık\n(120+)'])
tenure_sales_plot = df_merge.groupby(tenure_groups_plot)['basket_count'].sum()
bars = ax.bar(tenure_sales_plot.index.astype(str), tenure_sales_plot.values, color='#1abc9c')
ax.set_xlabel('Müşteri Sadakat Seviyesi (Tenure - Gün)', fontsize=12, fontweight='bold')
ax.set_ylabel('Toplam Satış Adedi', fontsize=12, fontweight='bold')
ax.set_title('Müşteri Sadakati Bazlı Satış Analizi', fontsize=14, fontweight='bold', pad=20)
# Değerleri çubukların üzerine yaz
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('grafik_6_musteri_sadakati_analizi.png', dpi=300, bbox_inches='tight')
print("   ✓ Grafik 6: Müşteri Sadakati Analizi kaydedildi (grafik_6_musteri_sadakati_analizi.png)")
plt.close()

# Grafik 7: Cinsiyet ve Yaş Grubu Kombinasyonu (Heatmap)
fig, ax = plt.subplots(figsize=(10, 6))
gender_age_pivot = df_merge.groupby(['age_group', 'sex'])['basket_count'].sum().unstack(fill_value=0)
im = ax.imshow(gender_age_pivot.values, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(gender_age_pivot.columns)))
ax.set_yticks(range(len(gender_age_pivot.index)))
ax.set_xticklabels(gender_age_pivot.columns)
ax.set_yticklabels(gender_age_pivot.index)
ax.set_xlabel('Cinsiyet', fontsize=12, fontweight='bold')
ax.set_ylabel('Yaş Grubu', fontsize=12, fontweight='bold')
ax.set_title('Cinsiyet ve Yaş Grubu Bazlı Satış Dağılımı (Heatmap)', fontsize=14, fontweight='bold', pad=20)
# Hücrelere değerleri yaz
for i in range(len(gender_age_pivot.index)):
    for j in range(len(gender_age_pivot.columns)):
        text = ax.text(j, i, f'{int(gender_age_pivot.values[i, j]):,}',
                       ha="center", va="center", color="black", fontsize=9, fontweight='bold')
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Toplam Satış Adedi', rotation=270, labelpad=20, fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('grafik_7_cinsiyet_yas_heatmap.png', dpi=300, bbox_inches='tight')
print("   ✓ Grafik 7: Cinsiyet ve Yaş Grubu Heatmap kaydedildi (grafik_7_cinsiyet_yas_heatmap.png)")
plt.close()

# ============================================================
# AŞAMA 4: RAPORLAMA VE İÇGÖRÜLER
# ============================================================

print("\n" + "="*80)
print("📋 AŞAMA 4: YÖNETİM RAPORU VE STRATEJİK ÖNERİLER")
print("="*80)

print("\n🎯 1. ÜRÜN STRATEJİSİ ÖNERİLERİ")
print("-"*80)

# En çok satan ürünleri analiz et
top_5_products = df_merge.groupby('product_id')['basket_count'].sum().sort_values(ascending=False).head(5)
total_sales = df_merge['basket_count'].sum()
top_5_percentage = (top_5_products.sum() / total_sales * 100)

print(f"\n📌 En Çok Satan 5 Ürün:")
for idx, (product_id, sales) in enumerate(top_5_products.items(), 1):
    percentage = (sales / total_sales * 100)
    print(f"   {idx}. Ürün {product_id}: {int(sales):,} adet (Toplam satışların %{percentage:.1f})")

print(f"\n✅ ÖNERİ: İlk 5 ürün toplam satışların %{top_5_percentage:.1f}'ini oluşturuyor.")
print(f"   → Bu ürünlerin stok yönetimini optimize edin")
print(f"   → Cross-selling ve up-selling stratejileri geliştirin")
print(f"   → Bu ürünlerde promosyon kampanyaları düzenleyin")

# Düşük performanslı ürünler
low_products = df_merge.groupby('product_id')['basket_count'].sum().sort_values().head(10)
print(f"\n⚠️  En Düşük Performans Gösteren 10 Ürün:")
for idx, (product_id, sales) in enumerate(low_products.items(), 1):
    print(f"   {idx}. Ürün {product_id}: {int(sales):,} adet")
print(f"\n✅ ÖNERİ: Düşük performanslı ürünler için:")
print(f"   → Ürün açıklamalarını ve görsellerini iyileştirin")
print(f"   → Fiyatlandırma stratejisini gözden geçirin")
print(f"   → Pazarlama çabalarını artırın veya ürünü katalogdan çıkarın")

print("\n🎯 2. MÜŞTERİ SEGMENTASYONİ VE HEDEFLEME")
print("-"*80)

# Cinsiyet analizi
gender_stats = df_merge.groupby('sex')['basket_count'].sum().sort_values(ascending=False)
dominant_gender = gender_stats.index[0]
dominant_percentage = (gender_stats.iloc[0] / gender_stats.sum() * 100)

print(f"\n📌 Cinsiyet Bazlı Analiz:")
for gender, sales in gender_stats.items():
    percentage = (sales / gender_stats.sum() * 100)
    print(f"   - {gender}: {int(sales):,} adet (%{percentage:.1f})")

print(f"\n✅ ÖNERİ: {dominant_gender} müşteriler toplam satışların %{dominant_percentage:.1f}'ini oluşturuyor.")
print(f"   → {dominant_gender} müşterilere özel kampanyalar geliştirin")
print(f"   → Diğer segmentleri büyütmek için targeted marketing yapın")

# Yaş grubu analizi
age_stats = df_merge.groupby('age_group')['basket_count'].sum().sort_values(ascending=False)
dominant_age = age_stats.index[0]
dominant_age_percentage = (age_stats.iloc[0] / age_stats.sum() * 100)

print(f"\n📌 Yaş Grubu Bazlı Analiz:")
for age_group, sales in age_stats.items():
    percentage = (sales / age_stats.sum() * 100)
    print(f"   - {age_group} yaş: {int(sales):,} adet (%{percentage:.1f})")

print(f"\n✅ ÖNERİ: {dominant_age} yaş grubu en yüksek satış hacmine sahip (%{dominant_age_percentage:.1f}).")
print(f"   → Bu yaş grubuna uygun ürün ve içerik stratejisi geliştirin")
print(f"   → Sosyal medya ve dijital pazarlama kanallarını optimize edin")

print("\n🎯 3. ZAMANLAMA VE KAMPANYA STRATEJİSİ")
print("-"*80)

# Haftanın günü analizi
day_order_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_labels_tr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
day_stats = df_merge.groupby('day_of_week')['basket_count'].sum().reindex(day_order_en)
best_day_idx = day_stats.idxmax()
best_day_tr = day_labels_tr[day_order_en.index(best_day_idx)]
worst_day_idx = day_stats.idxmin()
worst_day_tr = day_labels_tr[day_order_en.index(worst_day_idx)]

print(f"\n📌 Haftanın Günü Analizi:")
for day_en, day_tr in zip(day_order_en, day_labels_tr):
    sales = day_stats[day_en]
    percentage = (sales / day_stats.sum() * 100)
    print(f"   - {day_tr}: {int(sales):,} adet (%{percentage:.1f})")

print(f"\n✅ ÖNERİ:")
print(f"   → En yüksek satış günü: {best_day_tr}")
print(f"     • Bu günlerde özel kampanyalar ve flash sale'ler düzenleyin")
print(f"     • Stok ve lojistik kapasiteyi artırın")
print(f"   → En düşük satış günü: {worst_day_tr}")
print(f"     • Bu günlerde özel indirimler ve promosyonlar yapın")
print(f"     • Email ve SMS kampanyaları gönderin")

print("\n🎯 4. MÜŞTERİ SADAKATİ VE RETENTION STRATEJİSİ")
print("-"*80)

# Tenure analizi
tenure_groups_analysis = pd.cut(df_merge['tenure'], bins=[0, 60, 90, 120, 150], labels=['Yeni (0-60)', 'Orta (61-90)', 'Sadık (91-120)', 'Çok Sadık (120+)'])
tenure_stats = df_merge.groupby(tenure_groups_analysis)['basket_count'].agg(['sum', 'count'])
tenure_stats.columns = ['Toplam Satış', 'Sipariş Sayısı']

print(f"\n📌 Müşteri Sadakat Analizi:")
for idx, row in tenure_stats.iterrows():
    percentage = (row['Toplam Satış'] / tenure_stats['Toplam Satış'].sum() * 100)
    avg_order = row['Toplam Satış'] / row['Sipariş Sayısı']
    print(f"   - {idx}:")
    print(f"     Toplam Satış: {int(row['Toplam Satış']):,} adet (%{percentage:.1f})")
    print(f"     Ortalama Sepet: {avg_order:.1f} adet")

most_loyal = tenure_stats['Toplam Satış'].idxmax()
print(f"\n✅ ÖNERİ:")
print(f"   → En yüksek satış grubu: {most_loyal}")
print(f"   → Yeni müşteriler için:")
print(f"     • Onboarding programları ve hoş geldin kampanyaları")
print(f"     • İlk alışveriş indirimleri")
print(f"   → Sadık müşteriler için:")
print(f"     • Loyalty programları ve VIP statüler")
print(f"     • Özel erişim ve early-bird kampanyalar")
print(f"     • Referral programları")

print("\n🎯 5. GENEL İŞ STRATEJİSİ ÖNERİLERİ")
print("-"*80)

avg_basket = df_merge['basket_count'].mean()
total_customers = df_merge['customer_id'].nunique()
total_products = df_merge['product_id'].nunique()

print(f"\n📌 Önemli Metrikler:")
print(f"   - Ortalama sepet büyüklüğü: {avg_basket:.2f} adet")
print(f"   - Toplam aktif müşteri: {total_customers:,}")
print(f"   - Toplam aktif ürün: {total_products:,}")

print(f"\n✅ STRATEJİK ÖNERİLER:")
print(f"\n   1. SATIŞ ARTIRMA:")
print(f"      → Sepet ortalamasını artırmak için bundle kampanyaları")
print(f"      → Minimum sipariş tutarı için kargo bedava kampanyaları")
print(f"      → Upselling ve cross-selling algoritmaları geliştirin")

print(f"\n   2. MÜŞTERİ DENEYİMİ:")
print(f"      → Personalization ve öneri sistemleri kurun")
print(f"      → Mobil uygulama ve web sitesi UX'ini optimize edin")
print(f"      → Müşteri geri bildirim sistemleri oluşturun")

print(f"\n   3. PAZARLAMA:")
print(f"      → Dominant segmentlere özel kampanyalar geliştirin")
print(f"      → Email marketing ve retargeting stratejileri")
print(f"      → Sosyal medya influencer işbirlikleri")

print(f"\n   4. OPERASYONEL:")
print(f"      → Yoğun günlerde lojistik kapasiteyi artırın")
print(f"      → Popüler ürünlerde stok yönetimini optimize edin")
print(f"      → Veri analitiği ve BI araçlarına yatırım yapın")

print("\n" + "="*80)
print("✅ ANALİZ TAMAMLANDI!")
print("="*80)
print("\n📁 Oluşturulan Dosyalar:")
print("   1. grafik_1_top_urunler.png")
print("   2. grafik_2_cinsiyet_analizi.png")
print("   3. grafik_3_yas_grubu_analizi.png")
print("   4. grafik_4_gunluk_satis_trendi.png")
print("   5. grafik_5_haftanin_gunu_analizi.png")
print("   6. grafik_6_musteri_sadakati_analizi.png")
print("   7. grafik_7_cinsiyet_yas_heatmap.png")
print("\n🎉 Raporunuz başarıyla oluşturuldu!")
print("="*80)
