import shap
import pandas as pd
import traceback
from app.core.model_loader import ml_system

def calculate_shap_values(X_input: pd.DataFrame, predicted_class_index: int) -> list:
    """
    Menghitung nilai SHAP untuk menjelaskan kontribusi masing-masing fitur.
    Dilengkapi dengan XGBoost Booster Extraction dan Error Tracer.
    """
    try:
        # FIX 1: Ekstrak "mesin asli" (Booster) dari XGBClassifier agar SHAP tidak bingung
        booster = ml_system.model.get_booster()
        
        # FIX 2: Sinkronisasi nama kolom secara paksa antara DataFrame dan Model
        booster.feature_names = X_input.columns.tolist()

        # Gunakan TreeExplainer pada Booster, bukan pada bungkus luarnya
        explainer = shap.TreeExplainer(booster)
        
        # FIX 3: Matikan check_additivity (Penyebab utama crash pada model Multiclass)
        shap_values = explainer.shap_values(X_input, check_additivity=False)
        
        # Ekstraksi Array Multiclass
        if isinstance(shap_values, list):
            class_shap_values = shap_values[predicted_class_index][0]
        else:
            if len(shap_values.shape) == 3:
                 # Format Shape: (n_samples, n_features, n_classes)
                 class_shap_values = shap_values[0, :, predicted_class_index]
            else:
                 class_shap_values = shap_values[0]

        # Gabungkan nama kolom dengan nilai kontribusinya
        feature_names = X_input.columns.tolist()
        shap_dict = dict(zip(feature_names, class_shap_values))
        
        # Urutkan dari kontribusi paling besar
        sorted_shap = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
        
        # Format ke bentuk Dictionary untuk Frontend
        top_factors = []
        for feat, val in sorted_shap[:5]: 
            clean_name = feat.replace("sektor_industri_", "Sektor: ").replace("risiko_kritis_", "Risiko: ")
            clean_name = clean_name.replace("_", " ").title()

            top_factors.append({
                "faktor": clean_name[:30], # Batasi 30 huruf agar UI tidak berantakan
                "kontribusi": round(float(val), 4)
            })
            
        return top_factors

    except Exception as e:
        # Tampilkan error MERAH MENYALA di terminal agar tidak menjadi Silent Error lagi
        print("\n" + ""*25)
        print("FATAL ERROR DI SHAP EXPLAINER:")
        print(traceback.format_exc())
        print(""*25 + "\n")
        
        # Kirim pesan error ke UI agar Anda tahu ini gagal
        return [{
            "faktor": "Error: Cek Terminal Backend",
            "kontribusi": 0.0
        }]