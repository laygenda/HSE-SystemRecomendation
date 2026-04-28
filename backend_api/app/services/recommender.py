# File ini bertugas menerima data dari API, melakukan One-Hot Encoding, memprediksi menggunakan XGBoost, dan meracik rekomendasi berdasarkan logika CARS (Context-Aware).
import pandas as pd
from app.models.schemas import PredictionRequest, RecommendationResponse
from app.core.model_loader import ml_system

def process_prediction_and_cars(data: PredictionRequest) -> RecommendationResponse:
    # 1. Konversi input ke DataFrame
    df_input = pd.DataFrame([data.model_dump()])
    
    # 2. Preprocessing (One-Hot Encoding) sesuai saat training
    X_input = pd.get_dummies(df_input, columns=['sektor_industri', 'risiko_kritis'])
    X_input = X_input.reindex(columns=ml_system.kolom_fitur, fill_value=0)
    
    # 3. Prediksi XGBoost
    prediksi_probabilitas = ml_system.model.predict_proba(X_input)[0]
    kelas_terpilih_idx = int(ml_system.model.predict(X_input)[0])
    
    # Translate kembali ke Level (misal: "Level IV")
    prediksi_keparahan = ml_system.le_target.inverse_transform([kelas_terpilih_idx])[0]
    skor_risiko = float(prediksi_probabilitas[kelas_terpilih_idx] * 100)
    
    # 4. Logika CARS (Context-Aware Recommendation)
    # Ini adalah contoh Rule-Based Knowledge Recommender
    rekomendasi = "Lanjutkan pekerjaan sesuai SOP."
    actions = ["Gunakan APD standar", "Patuhi prosedur kerja"]
    
    is_high_wind = data.kecepatan_angin_kmh > 30
    is_fatigued = data.jam_kerja_sebelum_insiden > 8
    
    if prediksi_keparahan in ["Level IV", "Level V"]:
        rekomendasi = "PERINGATAN KRITIS: Risiko Kecelakaan Sangat Tinggi!"
        actions = ["Tunda pekerjaan berisiko tinggi segera"]
        
        # Konteks Cuaca & Kelelahan
        if is_high_wind:
            actions.append("Hentikan operasi lifting (pengangkatan) karena angin ekstrem.")
        if is_fatigued:
            actions.append("Rotasi kru sekarang, tingkat fatigue terlalu tinggi.")
            
    elif prediksi_keparahan in ["Level II", "Level III"]:
        rekomendasi = "Waspada: Risiko Sedang terdeteksi."
        actions = ["Lakukan Toolbox Meeting sebelum mulai", "Tambah pengawasan safety officer"]

    return RecommendationResponse(
        risk_level=prediksi_keparahan,
        confidence_score=round(skor_risiko, 2),
        recommendation_text=rekomendasi,
        immediate_actions=actions
    )