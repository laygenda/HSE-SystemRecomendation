from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.model_loader import ml_system
from app.models.schemas import PredictionRequest, RecommendationResponse
from app.services.recommender import process_prediction_and_cars

# Lifespan: Berjalan saat server start dan mati saat server stop
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML Model
    ml_system.load_models()
    yield
    # Shutdown logic (jika ada) bisa ditaruh di sini

app = FastAPI(
    title="HSE Intervention Recommender API",
    description="API MLOps untuk Sistem Rekomendasi Keselamatan Kerja",
    version="1.0.0",
    lifespan=lifespan
)

# Konfigurasi CORS agar Next.js bisa mengambil data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Di production ganti dengan URL Next.js ("http://localhost:3000")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "HSE AI Backend is running!"}

@app.post("/api/recommend", response_model=RecommendationResponse)
def get_recommendation(request_data: PredictionRequest):
    """
    Endpoint utama untuk menerima data cuaca & pekerjaan, 
    lalu mengembalikan hasil klasifikasi XGBoost dan rekomendasi CARS.
    """
    hasil = process_prediction_and_cars(request_data)
    return hasil