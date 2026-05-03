import pandas as pd
from app.models.schemas import PredictionRequest, RecommendationResponse
from app.core.model_loader import ml_system
from app.services.explainer import calculate_shap_values

def process_prediction_and_cars(data: PredictionRequest) -> RecommendationResponse:
    # 1. Konversi input ke DataFrame
    df_input = pd.DataFrame([data.model_dump()])
    
    # 2. Preprocessing (One-Hot Encoding)
    X_input = pd.get_dummies(df_input, columns=['sektor_industri', 'risiko_kritis'])
    X_input = X_input.reindex(columns=ml_system.kolom_fitur, fill_value=0)
    
    # FIX SHAP: Ubah seluruh nilai input menjadi tipe Float agar SHAP Explainer tidak crash
    # karena membaca nilai boolean (True/False) dari hasil get_dummies
    X_input = X_input.astype(float) 
    
    # 3. Prediksi XGBoost
    prediksi_probabilitas = ml_system.model.predict_proba(X_input)[0]
    kelas_terpilih_idx = int(ml_system.model.predict(X_input)[0])
    
    # Translate kembali ke Level (Output asli dari datasetmu adalah "I", "II", "III", "IV", "V", "VI")
    prediksi_keparahan = ml_system.le_target.inverse_transform([kelas_terpilih_idx])[0]
    skor_risiko = float(prediksi_probabilitas[kelas_terpilih_idx] * 100)
    
    # 4. Hitung Explainability (SHAP)
    penjelasan_shap = calculate_shap_values(X_input, kelas_terpilih_idx)

    # 5. Logika CARS (Context-Aware Recommendation)
    # Default = Aman
    rekomendasi = "Lanjutkan pekerjaan sesuai SOP."
    actions = ["Gunakan APD standar", "Patuhi prosedur kerja"]
    
    is_high_wind = data.kecepatan_angin_kmh > 30
    is_fatigued = data.jam_kerja_sebelum_insiden > 8
    
    # FIX CARS LOGIC: Sesuaikan dengan string asli dari target modelmu (misal: "IV", bukan "Level IV")
    if prediksi_keparahan in ["IV", "V", "VI"]:
        rekomendasi = "⚠ PERINGATAN KRITIS: Risiko Kecelakaan Sangat Tinggi!"
        actions = ["Tunda pekerjaan berisiko tinggi segera"]
        
        if is_high_wind:
            actions.append(f"Hentikan operasi lifting (pengangkatan) karena angin ekstrem ({data.kecepatan_angin_kmh} km/h).")
        if is_fatigued:
            actions.append(f"Rotasi kru sekarang, pekerja telah beraktivitas {data.jam_kerja_sebelum_insiden} jam (Fatigue Tinggi).")
            
    elif prediksi_keparahan in ["II", "III"]:
        rekomendasi = "Waspada: Risiko Sedang terdeteksi."
        actions = ["Lakukan Toolbox Meeting sebelum mulai", "Tambah pengawasan safety officer"]

    # Tambahkan prefiks 'Level ' hanya untuk tampilan cantik di UI (misal: "Level IV")
    ui_risk_level = f"Level {prediksi_keparahan}" if not prediksi_keparahan.startswith("Level") else prediksi_keparahan

    return RecommendationResponse(
        risk_level=ui_risk_level,
        confidence_score=round(skor_risiko, 2),
        recommendation_text=rekomendasi,
        immediate_actions=actions,
        explainability=penjelasan_shap
    )