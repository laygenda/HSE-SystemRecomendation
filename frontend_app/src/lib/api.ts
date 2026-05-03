import axios from 'axios';

// 1. Definisikan tipe data sesuai dengan response dari FastAPI (Backend)
export interface ShapExplanation {
  faktor: string;
  kontribusi: number;
}

export interface RecommendationResponse {
  risk_level: string;
  confidence_score: number;
  recommendation_text: string;
  immediate_actions: string[];
  explainability: ShapExplanation[];
}

export interface PredictionRequest {
  sektor_industri: string;
  risiko_kritis: string;
  jam_kerja_sebelum_insiden: number;
  suhu_c: number;
  kecepatan_angin_kmh: number;
}

// 2. Konfigurasi Axios
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 3. Fungsi khusus untuk menembak endpoint /api/recommend
export const getHSERecommendation = async (data: PredictionRequest): Promise<RecommendationResponse> => {
  try {
    const response = await apiClient.post<RecommendationResponse>('/api/recommend', data);
    return response.data;
  } catch (error) {
    console.error("Gagal mengambil data dari Backend AI:", error);
    throw error;
  }
};

//  Tipe data untuk Peta dari PostgreSQL 
export interface MapIncidentData {
  id_insiden: number;
  sektor_industri: string;
  risiko_kritis: string;
  suhu_c: number;
  angin_kmh: number;
  jam_kerja_sebelum_insiden: number;
  potensi_keparahan: string;
  latitude: number;
  longitude: number;
}

// Fungsi untuk mengambil data peta
export const getLiveMapData = async (): Promise<MapIncidentData[]> => {
  try {
    const response = await apiClient.get<MapIncidentData[]>('/api/live-map-data');
    return response.data;
  } catch (error) {
    console.error("Gagal mengambil data peta live:", error);
    return [];
  }
};