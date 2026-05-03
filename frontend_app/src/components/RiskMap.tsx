"use client";

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { MapIncidentData } from '../lib/api';

// Komponen helper agar peta otomatis pindah lokasi (FlyTo) saat data berubah
const MapController = ({ center }: { center: [number, number] }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, map.getZoom());
  }, [center, map]);
  return null;
};

interface RiskMapProps {
  data: MapIncidentData[];
  onMarkerClick: (incident: MapIncidentData) => void;
}

const RiskMap: React.FC<RiskMapProps> = ({ data, onMarkerClick }) => {
  // Pusat peta diubah ke titik ASLI data tambang IHM Stefanini (Minas Gerais, Brazil)
  const defaultCenter: [number, number] = [-19.93, -43.97]; 
  
  // Jika ada data, pusatkan peta ke titik data pertama
  const currentCenter: [number, number] = data.length > 0 
    ? [data[0].latitude, data[0].longitude] 
    : defaultCenter;

  return (
    <div className="w-full h-full rounded-lg overflow-hidden z-0">
      <MapContainer 
        center={currentCenter} 
        zoom={10} // Zoom diperbesar dari 5 ke 10 agar area tambang lebih jelas
        style={{ height: '100%', width: '100%', zIndex: 0 }}
        zoomControl={false}
      >
        <MapController center={currentCenter} />
        
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap'
        />
        
        {data.map((incident) => (
          <CircleMarker 
            key={incident.id_insiden}
            center={[incident.latitude, incident.longitude]} 
            radius={15} 
            pathOptions={{ 
              color: ['IV', 'V', 'VI'].includes(incident.potensi_keparahan) ? '#ef4444' : '#f59e0b', 
              fillColor: ['IV', 'V', 'VI'].includes(incident.potensi_keparahan) ? '#f87171' : '#fcd34d', 
              fillOpacity: 0.7 
            }}
            eventHandlers={{
              click: () => onMarkerClick(incident),
            }}
          >
            <Popup className="font-sans">
              <div className="text-sm">
                <strong className="text-slate-800">Sektor: {incident.sektor_industri}</strong><br/>
                <span className="text-slate-600 text-xs">Bahaya: {incident.risiko_kritis}</span><br/>
                <hr className="my-1" />
                <span className="text-slate-500 text-xs">Angin: {incident.angin_kmh} km/h | Suhu: {incident.suhu_c}°C</span><br/>
                <button 
                  onClick={() => onMarkerClick(incident)}
                  className="mt-2 text-xs bg-blue-600 text-white px-2 py-1 rounded w-full hover:bg-blue-700 transition-colors"
                >
                  Analisis Risiko dengan AI
                </button>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
};

export default RiskMap;