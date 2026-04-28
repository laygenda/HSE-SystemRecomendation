import os
import sys
import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib

# ==========================================
# 0. KONFIGURASI LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# ==========================================
# 1. PATH YANG BENAR (SUDAH DI DALAM ml_experiments)
# ==========================================
# Jika script dijalankan dari folder:
# HSE-recomendation/ml_experiments/
# maka output langsung ke:
# HSE-recomendation/ml_experiments/models/

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "models"

# Pakai folder yang sudah ada
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_ml_pipeline():
    logger.info("=== Mulai Phase 2: Pipeline Training XGBoost ===")

    # ==========================================
    # 2. AMBIL DATA DATABASE
    # ==========================================
    try:
        logger.info("Menghubungkan ke PostgreSQL...")

        DATABASE_URI = "postgresql://postgres:root@localhost:5432/hse_db"
        engine = create_engine(DATABASE_URI)

        query = """
        SELECT 
            p.sektor_industri, 
            p.risiko_kritis, 
            c.suhu_c, 
            c.kelembaban_pct, 
            c.angin_kmh, 
            f.jam_kerja_sebelum_insiden, 
            f.potensi_keparahan 
        FROM fact_insiden f
        JOIN dim_pekerjaan p ON f.id_pekerjaan = p.id_pekerjaan
        JOIN dim_cuaca c ON f.id_cuaca = c.id_cuaca
        """

        df = pd.read_sql(query, engine)

        logger.info(f"Berhasil mengambil {len(df)} data.")

    except Exception as e:
        logger.error(f"Gagal ambil data: {e}")
        sys.exit(1)

    # ==========================================
    # 3. PREPROCESSING
    # ==========================================
    try:
        logger.info("Feature Engineering...")

        le_target = LabelEncoder()
        df["target"] = le_target.fit_transform(df["potensi_keparahan"])

        X = df.drop(columns=["potensi_keparahan", "target"])
        y = df["target"]

        X = pd.get_dummies(
            X,
            columns=["sektor_industri", "risiko_kritis"]
        )

        kolom_fitur = list(X.columns)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        logger.info(
            f"Train: {len(X_train)} | Test: {len(X_test)}"
        )

    except Exception as e:
        logger.error(f"Gagal preprocessing: {e}")
        sys.exit(1)

    # ==========================================
    # 4. TRAINING MODEL
    # ==========================================
    try:
        logger.info("Training XGBoost...")

        model = xgb.XGBClassifier(
            objective="multi:softprob",
            eval_metric="mlogloss",
            use_label_encoder=False,
            random_state=42
        )

        model.fit(X_train, y_train)

        logger.info("Training selesai.")

    except Exception as e:
        logger.error(f"Gagal training: {e}")
        sys.exit(1)

    # ==========================================
    # 5. EVALUASI & SIMPAN
    # ==========================================
    try:
        akurasi = model.score(X_test, y_test)

        logger.info(f"Akurasi: {akurasi * 100:.2f}%")

        logger.info(f"Menyimpan ke: {OUTPUT_DIR}")

        joblib.dump(model, OUTPUT_DIR / "xgb_model.pkl")
        joblib.dump(kolom_fitur, OUTPUT_DIR / "model_columns.pkl")
        joblib.dump(le_target, OUTPUT_DIR / "target_encoder.pkl")

        logger.info("Semua file berhasil disimpan.")

    except Exception as e:
        logger.error(f"Gagal simpan model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_ml_pipeline()