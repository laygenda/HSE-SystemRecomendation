from fastapi import FastAPI, Depends # BARU: import Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# BARU: Import alat untuk akses database
from sqlalchemy.orm import Session
from sqlalchemy import text
import random

from app.core.model_loader import ml_system
from app.core.database import get_db # BARU: Import koneksi DB
from app.models.schemas import PredictionRequest, RecommendationResponse, MapIncidentData
from app.services.recommender import process_prediction_and_cars

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_system.load_models()
    yield

app = FastAPI(
    title="HSE Intervention Recommender API",
    description="API MLOps untuk Sistem Rekomendasi Keselamatan Kerja",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "HSE AI Backend is running!"}

@app.post("/api/recommend", response_model=RecommendationResponse)
def get_recommendation(request_data: PredictionRequest):
    hasil = process_prediction_and_cars(request_data)
    return hasil

# ========================================================
# BARU: ENDPOINT UNTUK REAL-TIME GEOSPATIAL MAP (OPSI B)
# ========================================================
@app.get("/api/live-map-data", response_model=list[MapIncidentData])
def get_live_map_data(db: Session = Depends(get_db)):
    """
    Mengambil 5 data insiden berisiko terbaru dari PostgreSQL hse_db.
    """
    # Query persis seperti yang sering dilakukan Data Engineer
    query = text("""
        SELECT 
            f.id_insiden, p.sektor_industri, p.risiko_kritis, 
            c.suhu_c, c.angin_kmh, f.jam_kerja_sebelum_insiden, 
            f.potensi_keparahan 
        FROM fact_insiden f
        JOIN dim_pekerjaan p ON f.id_pekerjaan = p.id_pekerjaan
        JOIN dim_cuaca c ON f.id_cuaca = c.id_cuaca
        ORDER BY f.id_insiden DESC
        LIMIT 5
    """)
    
    result = db.execute(query).mappings().all()
    
    # MENGGUNAKAN KOORDINAT ASLI DARI DATASET OPEN-METEO (Brazil)
    # 19.93S 43.97W
    base_lat = -19.93
    base_lng = -43.97
    
    map_data = []
    for row in result:
        map_data.append({
            "id_insiden": row["id_insiden"],
            "sektor_industri": row["sektor_industri"],
            "risiko_kritis": row["risiko_kritis"],
            "suhu_c": float(row["suhu_c"]),
            "angin_kmh": float(row["angin_kmh"]),
            "jam_kerja_sebelum_insiden": int(row["jam_kerja_sebelum_insiden"]),
            "potensi_keparahan": row["potensi_keparahan"],
            # Penyebaran radius dikurangi dari 0.5 menjadi 0.05 derajat agar 
            # titik-titiknya masih berada dalam satu kawasan industri tambang yang sama
            "latitude": base_lat + random.uniform(-0.05, 0.05), 
            "longitude": base_lng + random.uniform(-0.05, 0.05)
        })
        
    return map_data