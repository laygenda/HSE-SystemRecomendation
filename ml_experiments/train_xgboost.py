import os
import sys
import logging
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib

# ==========================================
# 0. KONFIGURASI LOGGING PROFESIONAL
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Tentukan folder output agar file tidak berantakan
OUTPUT_DIR = "ml_experiments"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_ml_pipeline():
    logger.info("=== Mulai Phase 2: Pipeline Training XGBoost ===")
    
    # ==========================================
    # 1. PULL DATA DARI DATABASE
    # ==========================================
    try:
        logger.info("Menghubungkan ke database PostgreSQL...")
        DATABASE_URI = 'postgresql://postgres:root@localhost:5432/hse_db'
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
        logger.info(f"Berhasil menarik {len(df)} baris data untuk dilatih.")
        
    except Exception as e:
        logger.error(f"GAGAL menarik data dari database! Error: {e}")
        sys.exit(1) # Hentikan program jika gagal ambil data

    # ==========================================
    # 2. FEATURE ENGINEERING (Persiapan Data)
    # ==========================================
    try:
        logger.info("Memulai Feature Engineering (Preprocessing)...")
        le_target = LabelEncoder()
        df['target'] = le_target.fit_transform(df['potensi_keparahan'])

        X = df.drop(columns=['potensi_keparahan', 'target'])
        y = df['target']

        X = pd.get_dummies(X, columns=['sektor_industri', 'risiko_kritis'])
        kolom_fitur = list(X.columns)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        logger.info(f"Data dipecah: {len(X_train)} data training, {len(X_test)} data testing.")
        
    except Exception as e:
        logger.error(f"GAGAL melakukan Feature Engineering! Error: {e}")
        sys.exit(1)

    # ==========================================
    # 3. TRAINING MODEL XGBOOST
    # ==========================================
    try:
        logger.info("Melatih model algoritma XGBoost Classifier...")
        model = xgb.XGBClassifier(
            objective='multi:softprob', 
            eval_metric='mlogloss', 
            use_label_encoder=False,
            random_state=42
        )
        model.fit(X_train, y_train)
        logger.info("Proses training model selesai dengan sukses.")
        
    except Exception as e:
        logger.error(f"GAGAL melatih model XGBoost! Error: {e}")
        sys.exit(1)

    # ==========================================
    # 4. EVALUASI & EXPORT MODEL
    # ==========================================
    try:
        logger.info("Mengevaluasi akurasi model pada data testing...")
        akurasi = model.score(X_test, y_test)
        logger.info(f"Evaluasi Selesai! Akurasi Model: {akurasi * 100:.2f}%")

        logger.info(f"Menyimpan file model ke folder '{OUTPUT_DIR}'...")
        # Simpan file langsung ke dalam folder ml_experiments
        joblib.dump(model, os.path.join(OUTPUT_DIR, 'xgb_model.pkl'))
        joblib.dump(kolom_fitur, os.path.join(OUTPUT_DIR, 'model_columns.pkl'))
        joblib.dump(le_target, os.path.join(OUTPUT_DIR, 'target_encoder.pkl'))
        
        logger.info("SELURUH PIPELINE PHASE 2 SELESAI DENGAN SUKSES!")
        
    except Exception as e:
        logger.error(f"GAGAL menyimpan file model! Error: {e}")
        sys.exit(1)

# Trigger utama untuk menjalankan script
if __name__ == "__main__":
    run_ml_pipeline()