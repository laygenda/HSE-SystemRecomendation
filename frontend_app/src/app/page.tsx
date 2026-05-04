"use client";

import React, { useState, useEffect } from 'react';
import { getHSERecommendation, RecommendationResponse, PredictionRequest, getLiveMapData, MapIncidentData, getWeeklyTrend, WeeklyTrendData } from '../lib/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LineChart, Line, CartesianGrid, Legend } from 'recharts';
import dynamic from 'next/dynamic'; 

const DynamicRiskMap = dynamic(() => import('../components/RiskMap'), { 
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center text-slate-400 bg-slate-50 animate-pulse rounded">Memuat Peta Geospasial...</div>
});

export default function Dashboard() {
  const [aiData, setAiData] = useState<RecommendationResponse | null>(null);
  const [mapData, setMapData] = useState<MapIncidentData[]>([]);
  const [trendData, setTrendData] = useState<WeeklyTrendData[]>([]); 
  const [selectedIncident, setSelectedIncident] = useState<MapIncidentData | null>(null); 
  
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isMapLoading, setIsMapLoading] = useState<boolean>(true);

  // FIX UTAMA: Menarik data Peta dan Tren sekaligus secara paralel
  const fetchDashboardData = async () => {
    setIsMapLoading(true);
    try {
      const [mapResult, trendResult] = await Promise.all([
        getLiveMapData(),
        getWeeklyTrend()
      ]);

      setMapData(mapResult);
      setTrendData(trendResult); // Menyuntikkan data ke Line Chart!

      // Otomatis klik titik pertama saat web baru dibuka
      if (mapResult.length > 0) {
        handleAnalyzeIncident(mapResult[0]);
      }
    } catch (error) {
      console.error("Gagal mengambil data dashboard:", error);
    } finally {
      setIsMapLoading(false);
    }
  };

  const handleAnalyzeIncident = async (incident: MapIncidentData) => {
    setIsLoading(true);
    setSelectedIncident(incident); 
    
    try {
      const payload: PredictionRequest = {
        sektor_industri: incident.sektor_industri,
        risiko_kritis: incident.risiko_kritis,
        jam_kerja_sebelum_insiden: incident.jam_kerja_sebelum_insiden,
        suhu_c: incident.suhu_c,
        kecepatan_angin_kmh: incident.angin_kmh
      };

      const response = await getHSERecommendation(payload);
      setAiData(response);
    } catch (error) {
      console.error("Gagal memuat data AI");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans p-6">
      
      {/* HEADER SECTION */}
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 tracking-tight">HSE AI Recommendation Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">Real-time Context-Aware Risk Intervention System</p>
        </div>
        <button 
          onClick={fetchDashboardData}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          {isMapLoading ? "Syncing DB..." : "Refresh Dashboard"}
        </button>
      </header>

      {/* SECTION 1: KPI Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 h-24 flex flex-col justify-center">
          <span className="text-xs text-slate-500 font-semibold uppercase">Risk Level</span>
          <span className={`text-xl font-bold mt-1 ${aiData?.risk_level.includes('IV') || aiData?.risk_level.includes('V') || aiData?.risk_level.includes('VI') ? 'text-red-600' : 'text-amber-600'}`}>
            {isLoading ? "..." : aiData?.risk_level || "Unknown"}
          </span>
        </div>
        
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 h-24 flex flex-col justify-center">
          <span className="text-xs text-slate-500 font-semibold uppercase">AI Confidence</span>
          <span className="text-xl font-bold text-slate-800 mt-1">
            {isLoading ? "..." : `${aiData?.confidence_score}%`}
          </span>
        </div>
        
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 h-24 flex flex-col justify-center">
           <span className="text-xs text-slate-500 font-semibold uppercase">Current Wind</span>
           <span className={`text-xl font-bold mt-1 ${selectedIncident && selectedIncident.angin_kmh > 25 ? 'text-orange-500' : 'text-emerald-600'}`}>
              {selectedIncident ? `${selectedIncident.angin_kmh} km/h` : '--'}
           </span>
        </div>

        {[4, 5, 6].map((num) => (
           <div key={num} className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 h-24 flex items-center justify-center text-slate-300 font-medium text-sm">
             KPI {num}
           </div>
        ))}
      </section>

      {/* MAIN CONTENT GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
        
        {/* LEFT COLUMN */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-[400px] flex flex-col">
            <h2 className="text-lg font-semibold mb-4 border-b pb-2 flex justify-between">
              <span>Geospatial Risk Map</span>
              {isMapLoading && <span className="text-xs text-blue-500 font-normal animate-pulse">Syncing...</span>}
            </h2>
            <div className="flex-1 w-full bg-slate-50 rounded overflow-hidden z-0 border border-slate-200">
                 <DynamicRiskMap data={mapData} onMarkerClick={handleAnalyzeIncident} />
            </div>
          </section>

          <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-[300px] flex flex-col">
            <h2 className="text-lg font-semibold mb-4 border-b pb-2">Weekly Risk Trend</h2>
            <div className="flex-1 w-full text-sm min-h-[200px] relative">
              {trendData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="tanggal" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Line type="monotone" name="Risiko Tinggi (Level IV-VI)" dataKey="risiko_tinggi" stroke="#ef4444" strokeWidth={3} dot={{ r: 4, fill: '#ef4444', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                    <Line type="monotone" name="Risiko Rendah (Level I-III)" dataKey="risiko_rendah" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4, fill: '#f59e0b', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-slate-400 animate-pulse">Menghitung Agregasi Data...</div>
              )}
            </div>
          </section>
        </div>

        {/* RIGHT COLUMN */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          
          <section className="bg-slate-800 text-white p-6 rounded-xl shadow-md min-h-[400px] flex flex-col">
            <h2 className="text-lg font-semibold mb-4 border-b border-slate-600 pb-2">AI Intervention Panel</h2>
            {isLoading ? (
              <div className="flex-1 flex items-center justify-center text-slate-400 animate-pulse">Processing context...</div>
            ) : (
              <div className="flex flex-col gap-4">
                <div className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
                  <p className="text-sm text-slate-300 mb-1">Primary Recommendation:</p>
                  <p className="text-base font-medium text-white">{aiData?.recommendation_text}</p>
                </div>
                
                <div>
                  <p className="text-sm text-slate-400 mb-2 font-medium">Immediate Actions Required:</p>
                  <ul className="space-y-2">
                    {aiData?.immediate_actions?.map((action, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm bg-red-500/10 border border-red-500/20 text-red-200 p-2 rounded">
                        <span className="text-red-400">⚠</span> {action}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </section>

          <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-[300px] flex flex-col">
            <h2 className="text-lg font-semibold mb-4 border-b pb-2">Why This Risk Happened?</h2>
            <div className="flex-1 w-full text-sm min-h-[200px] relative">
              {isLoading ? (
                <div className="h-full flex items-center justify-center text-slate-400 animate-pulse">Menghitung SHAP Values...</div>
              ) : aiData?.explainability && aiData.explainability.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={aiData.explainability} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="faktor" type="category" width={120} tick={{ fontSize: 11, fill: '#475569' }} axisLine={false} tickLine={false} />
                    <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                    <Bar dataKey="kontribusi" radius={[0, 4, 4, 0]} barSize={20}>
                      {aiData.explainability.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.kontribusi > 0 ? '#ef4444' : '#3b82f6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-slate-400">Tidak ada data penjelas.</div>
              )}
            </div>
          </section>
        </div>

      </div>

      {/* FIX: Mengembalikan Section MLOps Monitoring yang tidak sengaja terhapus */}
      <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-lg font-semibold mb-4 border-b pb-2">MLOps Model Performance</h2>
        <div className="w-full h-32 bg-slate-50 border border-dashed border-slate-300 rounded flex items-center justify-center text-slate-400">[ MLOps Table Component ]</div>
      </section>

    </div>
  );
}