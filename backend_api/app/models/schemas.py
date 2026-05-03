from pydantic import BaseModel, Field
from typing import List

class PredictionRequest(BaseModel):
    # Data Pekerjaan
    sektor_industri: str = Field(..., example="Mining")
    risiko_kritis: str = Field(..., example="Pressed")
    jam_kerja_sebelum_insiden: int = Field(..., description="Simulasi tingkat fatigue", example=10)
    
    # Data Cuaca (Context)
    suhu_c: float = Field(..., example=33.5)
    kecepatan_angin_kmh: float = Field(..., example=35.0)

# untuk menampung SHAP 
class ShapExplanation(BaseModel):
    faktor: str
    kontribusi: float

class RecommendationResponse(BaseModel):
    risk_level: str
    confidence_score: float
    recommendation_text: str
    immediate_actions: List[str]
    explainability: List[ShapExplanation] = [] 
    
class MapIncidentData(BaseModel):
    id_insiden: int
    sektor_industri: str
    risiko_kritis: str
    suhu_c: float
    angin_kmh: float
    jam_kerja_sebelum_insiden: int
    potensi_keparahan: str
    latitude: float
    longitude: float