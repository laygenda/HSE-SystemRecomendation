import os
import joblib
import logging

logger = logging.getLogger(__name__)

class MLModelSystem:
    def __init__(self):
        self.model = None
        self.kolom_fitur = None
        self.le_target = None

    def load_models(self):
        # Path disesuaikan dengan posisi file ini dijalankan nanti
        # Mundur 2 folder ke root, lalu masuk ke ml_experiments
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        MODEL_DIR = os.path.join(BASE_DIR, "ml_experiments", "models")

        try:
            logger.info("Memuat Otak AI (XGBoost) ke memori...")
            self.model = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
            self.kolom_fitur = joblib.load(os.path.join(MODEL_DIR, "model_columns.pkl"))
            self.le_target = joblib.load(os.path.join(MODEL_DIR, "target_encoder.pkl"))
            logger.info("Model berhasil dimuat!")
        except Exception as e:
            logger.error(f"GAGAL memuat model: {e}")
            raise e

# Inisialisasi object global
ml_system = MLModelSystem()