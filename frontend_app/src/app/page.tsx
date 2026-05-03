import React from 'react';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans p-6">
      
      {/* HEADER SECTION */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">HSE AI Recommendation Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Real-time Context-Aware Risk Intervention System</p>
      </header>

      {/* SECTION 1: KPI Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {[1, 2, 3, 4, 5, 6].map((num) => (
           <div key={num} className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 h-24 flex items-center justify-center text-slate-400 font-medium">
             KPI Card {num}
           </div>
        ))}
      </section>

      {/* MAIN CONTENT GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
        
        {/* LEFT COLUMN (Span 8) */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-[400px]">
            <h2 className="text-lg font-semibold mb-4 border-b pb-2">Geospatial Risk Map</h2>
            <div className="w-full h-4/5 bg-slate-100 rounded flex items-center justify-center text-slate-400">[ Leaflet Map Component ]</div>
          </section>

          <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-[300px]">
            <h2 className="text-lg font-semibold mb-4 border-b pb-2">Weekly Risk Trend</h2>
            <div className="w-full h-4/5 bg-slate-100 rounded flex items-center justify-center text-slate-400">[ Recharts Line Component ]</div>
          </section>
        </div>

        {/* RIGHT COLUMN (Span 4) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <section className="bg-slate-800 text-white p-6 rounded-xl shadow-md h-[400px]">
            <h2 className="text-lg font-semibold mb-4 border-b border-slate-600 pb-2">AI Intervention Panel</h2>
            <div className="w-full h-4/5 rounded flex items-center justify-center text-slate-400">[ Recommendation Text ]</div>
          </section>

          <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-[300px]">
            <h2 className="text-lg font-semibold mb-4 border-b pb-2">Why This Risk Happened?</h2>
            <div className="w-full h-4/5 bg-slate-100 rounded flex items-center justify-center text-slate-400">[ SHAP Recharts Bar ]</div>
          </section>
        </div>

      </div>

      {/* SECTION 6: MLOps Monitoring */}
      <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-lg font-semibold mb-4 border-b pb-2">MLOps Model Performance</h2>
        <div className="w-full h-32 bg-slate-100 rounded flex items-center justify-center text-slate-400">[ MLOps Table Component ]</div>
      </section>

    </div>
  );
}