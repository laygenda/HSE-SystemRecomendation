# nenasrujab data yang dikirim dari frontend untuk prediksi dan rekomendasi

from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    # Data Pekerjaan
    sektor_industri: str = Field(..., example="Mining")
    risiko_kritis: str = Field(..., example="Pressed")
    jam_kerja_sebelum_insiden: int = Field(..., description="Simulasi tingkat fatigue", example=10)
    
    # Data Cuaca (Context)
    suhu_c: float = Field(..., example=33.5)
    kecepatan_angin_kmh: float = Field(..., example=35.0)

class RecommendationResponse(BaseModel):
    risk_level: str
    confidence_score: float
    recommendation_text: str
    immediate_actions: list[str]