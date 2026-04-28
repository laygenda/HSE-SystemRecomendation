import pandas as pd
import numpy as np
from sqlalchemy import create_engine

print("Mulai Proses Data Engineering (ETL Phase 1)...")

# ==========================================
# 1. EXTRACT (Menarik Data Mentah CSV)
# ==========================================
df_hse = pd.read_csv('C:\\Users\\laygenda surya putra\\Documents\\KULIAH\\Semester 4\\Rekomendasi Sistem\\Tugas\\HSE_recomendation\\data\\IHMStefanini_industrial_safety_and_health_database.csv')
df_weather = pd.read_csv('C:\\Users\\laygenda surya putra\\Documents\\KULIAH\\Semester 4\\Rekomendasi Sistem\\Tugas\\HSE_recomendation\\data\\open-meteo-19.93S43.97W860m.csv', skiprows=3, sep=';')

# ==========================================
# 2. TRANSFORM (Pembersihan & Penggabungan)
# ==========================================
print("Melakukan transformasi data...")
df_hse['waktu_kejadian'] = pd.to_datetime(df_hse['Data'])
df_weather['waktu_kejadian'] = pd.to_datetime(df_weather['time'])

# --- Bikin Data untuk: dim_pekerjaan ---
df_pekerjaan = df_hse[['Industry Sector', 'Risco Critico']].drop_duplicates().reset_index(drop=True)
df_pekerjaan['id_pekerjaan'] = df_pekerjaan.index + 1 
df_pekerjaan.rename(columns={'Industry Sector': 'sektor_industri', 'Risco Critico': 'risiko_kritis'}, inplace=True)
df_pekerjaan = df_pekerjaan[['id_pekerjaan', 'sektor_industri', 'risiko_kritis']]

df_hse = df_hse.merge(df_pekerjaan, left_on=['Industry Sector', 'Risco Critico'], 
                      right_on=['sektor_industri', 'risiko_kritis'], how='left')

# --- Bikin Data untuk: dim_cuaca ---
df_cuaca = df_weather.copy()
df_cuaca['id_cuaca'] = df_cuaca.index + 1
df_cuaca.rename(columns={
    'temperature_2m (°C)': 'suhu_c',
    'relative_humidity_2m (%)': 'kelembaban_pct',
    'precipitation (mm)': 'hujan_mm',
    'wind_speed_10m (km/h)': 'angin_kmh'
}, inplace=True)
df_cuaca = df_cuaca[['id_cuaca', 'waktu_kejadian', 'suhu_c', 'kelembaban_pct', 'hujan_mm', 'angin_kmh']]

# ---------------------------------------------------------
# PERBAIKAN: MEMBERSIHKAN FORMAT ANGKA YANG RUSAK KARENA EXCEL
# ---------------------------------------------------------
print("Membersihkan sisa format Excel yang rusak pada data cuaca...")
cols_to_clean = ['suhu_c', 'kelembaban_pct', 'hujan_mm', 'angin_kmh']

for col in cols_to_clean:
    # 1. Paksa ubah tipe datanya menjadi string/teks terlebih dahulu
    df_cuaca[col] = df_cuaca[col].astype(str)
    # 2. Ubah tanda koma menjadi titik (jika ada)
    df_cuaca[col] = df_cuaca[col].str.replace(',', '.', regex=False)
    # 3. Potong angka berlebih: Mengubah "26.00.00" menjadi "26.00" saja
    df_cuaca[col] = df_cuaca[col].str.extract(r'(\d+\.?\d*)')[0]
    # 4. Paksa konversi kembali menjadi Float murni
    df_cuaca[col] = pd.to_numeric(df_cuaca[col], errors='coerce')

# Isi kolom yang kosong (NaN) dengan angka 0 agar tidak error di Database
df_cuaca.fillna(0, inplace=True)
# ---------------------------------------------------------

df_hse = df_hse.merge(df_cuaca[['id_cuaca', 'waktu_kejadian']], on='waktu_kejadian', how='left')

# --- Bikin Data Fatigue (jam_kerja_sebelum_insiden) ---
np.random.seed(42) 
kondisi_parah = df_hse['Potential Accident Level'].isin(['IV', 'V', 'VI'])
df_hse.loc[kondisi_parah, 'jam_kerja_sebelum_insiden'] = np.random.randint(8, 13, size=kondisi_parah.sum())
df_hse.loc[~kondisi_parah, 'jam_kerja_sebelum_insiden'] = np.random.randint(1, 9, size=(~kondisi_parah).sum())

# --- Bikin Data untuk: fact_insiden ---
df_fact = df_hse[['waktu_kejadian', 'id_pekerjaan', 'id_cuaca', 'jam_kerja_sebelum_insiden', 
                  'Accident Level', 'Potential Accident Level']].copy()
df_fact['id_insiden'] = df_fact.index + 1
df_fact.rename(columns={'Accident Level': 'tingkat_aktual', 'Potential Accident Level': 'potensi_keparahan'}, inplace=True)
df_fact = df_fact.dropna(subset=['id_cuaca']) 

# ---------------------------------------------------------
# PERBAIKAN: PASTIKAN ID BERTIPE INTEGER (INT)
# ---------------------------------------------------------
df_fact['id_cuaca'] = df_fact['id_cuaca'].astype(int)
df_fact['id_pekerjaan'] = df_fact['id_pekerjaan'].astype(int)
df_fact['jam_kerja_sebelum_insiden'] = df_fact['jam_kerja_sebelum_insiden'].astype(int)
# ---------------------------------------------------------

df_fact = df_fact[['id_insiden', 'waktu_kejadian', 'id_pekerjaan', 'id_cuaca', 'jam_kerja_sebelum_insiden', 'tingkat_aktual', 'potensi_keparahan']]

# ==========================================
# 3. LOAD (Mengirim ke PostgreSQL pgAdmin)
# ==========================================
print("Menghubungkan ke database PostgreSQL...")
DATABASE_URI = 'postgresql://postgres:root@localhost:5432/hse_db'
engine = create_engine(DATABASE_URI)

# Kirim data ke tabel
print("Mengirim tabel dim_pekerjaan...")
df_pekerjaan.to_sql('dim_pekerjaan', engine, if_exists='append', index=False)

print("Mengirim tabel dim_cuaca...")
df_cuaca.to_sql('dim_cuaca', engine, if_exists='append', index=False)

print("Mengirim tabel fact_insiden...")
df_fact.to_sql('fact_insiden', engine, if_exists='append', index=False)

print("SUKSES! Seluruh data berhasil masuk ke PostgreSQL.")