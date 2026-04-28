import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 1.  inisialisasi aplikasi & cors
app = FastAPI(
    title="HSE Intervention Recommender API",
    description="API untuk memprediksi tingkat kecelakaan dan memberikan rekomendasi K3",
    version="1.0.0"
)

# Izinkan Next.js (Frontend) untuk mengakses API ini nanti
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Di production, ganti dengan URL Next.js Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load model machine learning yang sudah dilatih
MODEL_DIR = "ml_experiments"

try:
    print("Memuat Otak AI (Machine Learning Models)...")
    # Load file yang Anda buat di Phase 2
    model = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
    kolom_fitur = joblib.load(os.path.join(MODEL_DIR, "model_columns.pkl"))
    le_target = joblib.load(os.path.join(MODEL_DIR, "target_encoder.pkl"))
    print("Model berhasil dimuat ke memori!")
except Exception as e:
    print(f"GAGAL memuat model! Pastikan Anda menjalankan ini dari folder root proyek. Error: {e}")
    
# 3. SCHEMA VALIDASI INPUT (Pydantic)
# Ini memastikan data yang dikirim dari Frontend memiliki tipe data yang benar
class InputPekerjaan(BaseModel):
    sektor_industri: str = Field(..., example="Mining")
    risiko_kritis: str = Field(..., example="Pressed")
    suhu_c: float = Field(..., example=32.5)
    kelembaban_pct: float = Field(..., example=70.0)
    angin_kmh: float = Field(..., example=35.0)
    jam_kerja_sebelum_insiden: int = Field(..., example=10)
    
# 4. LOGIKA REKOMENDASI (Knowledge-Based CARS)
def generate_recommendation(keparahan: str, input_data: InputPekerjaan) -> str:
    # Jika sistem mendeteksi kecelakaan ringan/aman
    if keparahan in ["I", "II", "III"]:
        return "Aman. Silakan lanjutkan operasi sesuai SOP standar K3."
    
    # Jika sistem mendeteksi potensi kecelakaan PARAH (Level IV, V, VI)
    rekomendasi = "BAHAYA TINGGI! "
    
    # Aturan 1: Cek Angin
    if input_data.angin_kmh > 25.0:
        rekomendasi += f"Angin sangat kencang ({input_data.angin_kmh} km/h). Tunda pekerjaan di ketinggian (Lifting/Scaffolding). "
    
    # Aturan 2: Cek Kelelahan (Fatigue)
    if input_data.jam_kerja_sebelum_insiden > 8:
        rekomendasi += f"Kru sudah bekerja melebihi batas {input_data.jam_kerja_sebelum_insiden} jam (Risiko Fatigue). Segera lakukan ROTASI PEKERJA. "
        
    # Aturan 3: Default peringatan
    if input_data.angin_kmh <= 25.0 and input_data.jam_kerja_sebelum_insiden <= 8:
        rekomendasi += "Tinjau ulang izin kerja (Permit to Work) dan pastikan pengawasan diperketat di lapangan."
        
    return rekomendasi

# 5. ENDPOINT PREDIKSI (/predict)

@app.post("/predict")
def predict_risk(data: InputPekerjaan):
    try:
        # 1. Ubah JSON dari frontend menjadi DataFrame Pandas
        df_input = pd.DataFrame([data.dict()])
        
        # 2. Samakan perlakuan data seperti saat Phase 2 (One-Hot Encoding)
        X_input = pd.get_dummies(df_input, columns=['sektor_industri', 'risiko_kritis'])
        
        # 3. Kunci Utama MLOps: Samakan kolom dengan saat model dilatih (isi 0 jika kolom tidak ada)
        X_input = X_input.reindex(columns=kolom_fitur, fill_value=0)
        
        # 4. Prediksi dengan XGBoost
        prediksi_probabilitas = model.predict_proba(X_input)[0]
        kelas_terpilih_idx = int(model.predict(X_input)[0])
        
        # 5. Terjemahkan angka (0-5) kembali menjadi Level Keparahan (I - VI)
        prediksi_keparahan = le_target.inverse_transform([kelas_terpilih_idx])[0]
        
        # 6. Ambil persentase keyakinan model (Probabilitas Skor Risiko)
        skor_risiko = float(prediksi_probabilitas[kelas_terpilih_idx] * 100)
        
        # 7. Hasilkan Teks Rekomendasi
        teks_rekomendasi = generate_recommendation(prediksi_keparahan, data)
        
        # 8. Kirim kembali ke Frontend
        return {
            "status": "success",
            "prediksi_level_keparahan": prediksi_keparahan,
            "skor_risiko_persen": round(skor_risiko, 2),
            "rekomendasi_intervensi": teks_rekomendasi
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))