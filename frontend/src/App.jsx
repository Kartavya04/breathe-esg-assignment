import React, { useState, useEffect } from 'react';

export default function App() {
  const [reviewQueue, setReviewQueue] = useState([]);
  const [currentTab, setCurrentTab] = useState('pending'); // 🌟 'pending' or 'approved'
  const [selectedSource, setSelectedSource] = useState('SAP');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState('');

  // 1. FETCH THE QUEUE BASED ON THE ACTIVE TAB
  const fetchReviewQueue = async (tab = currentTab) => {
    try {
      const endpoint = tab === 'pending' 
        ? 'http://127.0.0.1:8000/api/review-queue/' 
        : 'http://127.0.0.1:8000/api/approved-ledger/'; // 🌟 Dynamic route targeting
        
      const response = await fetch(endpoint);
      if (response.ok) {
        const data = await response.json();
        setReviewQueue(data);
      }
    } catch (err) {
      console.error("Backend offline or connection refused:", err);
    }
  };

  // Re-fetch whenever the user switches tabs
  useEffect(() => {
    fetchReviewQueue(currentTab);
  }, [currentTab]);

  // 2. INGEST DATA DATASET
  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return alert("Please select a file first.");
    
    const formData = new FormData();
    formData.append('source_system', selectedSource);
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/upload/', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      
      if (response.ok) {
        setUploadMessage(`Success: ${result.message}`);
        setSelectedFile(null);
        setCurrentTab('pending'); // Force switch back to pending tab to see new rows
        await fetchReviewQueue('pending');
      } else {
        setUploadMessage(`Error: ${result.error}`);
      }
    } catch (err) {
      setUploadMessage("API transport error.");
    }
  };

  // 3. EXECUTE DATA ROW AUDIT ACTION
  const executeRowAction = async (rowId, actionType) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/review-queue/${rowId}/action/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionType }),
      });
      if (response.ok) {
        fetchReviewQueue(currentTab);
      }
    } catch (err) {
      alert("Action transmission failed.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 md:p-10">
      {/* GLOBAL BANNER */}
      <header className="mb-8 border-b border-slate-800 pb-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-emerald-400">
          BreatheESG Data Compliance Hub
        </h1>
        <p className="text-slate-400 mt-1 text-sm">
          Enterprise Environmental Audit Workflow Queue & Normalization Pipeline
        </p>
      </header>

      {/* DASHBOARD WORKSPACE SPLIT GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
        
        {/* SIDEBAR BLOCK: DATA INGESTION */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-md">
          <h2 className="text-lg font-bold mb-4 text-slate-200 border-b border-slate-700 pb-2">
            Data Ingestion Feed
          </h2>
          <form onSubmit={handleUploadSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Target Source Platform
              </label>
              <select 
                value={selectedSource} 
                onChange={(e) => setSelectedSource(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                <option value="SAP">SAP Procurement ERP (Scope 1)</option>
                <option value="UTILITY">Utility Portal CSV (Scope 2)</option>
                <option value="CONCUR">Concur Travel JSON (Scope 3)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Upload Raw Export Data
              </label>
              <input 
                type="file" 
                onChange={(e) => setSelectedFile(e.target.files[0])}
                className="w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-500/10 file:text-emerald-400 hover:file:bg-emerald-500/20 cursor-pointer"
              />
            </div>

            <button 
              type="submit" 
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-lg py-2.5 transition-all shadow-sm shadow-emerald-900/20"
            >
              Ingest & Process Pipeline
            </button>
          </form>

          {uploadMessage && (
            <div className={`mt-4 p-3 rounded-lg text-xs font-mono break-all ${
              uploadMessage.startsWith('Success') 
                ? 'bg-emerald-950/40 border border-emerald-800 text-emerald-400' 
                : 'bg-rose-950/40 border border-rose-800 text-rose-400'
            }`}>
              {uploadMessage}
            </div>
          )}
        </div>

        {/* DATA CONTAINER BLOCK: AUDIT TRACK STREAM */}
        <div className="lg:col-span-3 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-md">
          
          {/* 🌟 TAB TOGGLE SWITCH BANNER */}
          <div className="flex gap-4 mb-4 border-b border-slate-700/60 pb-3">
            <button
              onClick={() => setCurrentTab('pending')}
              className={`px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${
                currentTab === 'pending'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-400 hover:bg-slate-700/40 hover:text-slate-200'
              }`}
            >
              Pending Audit Queue
            </button>
            <button
              onClick={() => setCurrentTab('approved')}
              className={`px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${
                currentTab === 'approved'
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:bg-slate-700/40 hover:text-slate-200'
              }`}
            >
              Approved Ledger History Log
            </button>
          </div>
          
          {reviewQueue.length === 0 ? (
            <div className="text-center py-16 border border-dashed border-slate-700 rounded-xl text-slate-500 text-sm">
              {currentTab === 'pending' 
                ? "No line transactions pending approval review balances." 
                : "No verified historical records found in the approved ledger workspace."}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-700 text-slate-400 font-semibold">
                    <th className="py-3 px-4">Line Source ID</th>
                    <th className="py-3 px-4">Activity Stream</th>
                    <th className="py-3 px-4 text-right">Normalized Metric</th>
                    <th className="py-3 px-4 text-right">Calculated Footprint</th>
                    <th className="py-3 px-4">Reporting Date</th>
                    {currentTab === 'pending' && <th className="py-3 px-4 text-center">Actions</th>}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/40">
                  {reviewQueue.map((row) => (
                    <tr 
                      key={row.id} 
                      className={`transition-colors ${row.has_data_anomaly ? 'bg-amber-500/5 hover:bg-amber-500/10' : 'hover:bg-slate-700/20'}`}
                    >
                      <td className="py-3.5 px-4 font-mono font-medium text-slate-300">
                        {row.source_system_line_id}
                        {row.has_data_anomaly && (
                          <span className="block text-[11px] text-amber-400 font-sans mt-0.5 font-normal">
                            ⚠ {row.anomaly_explanation}
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold mr-2 ${
                          row.ghg_scope === 1 ? 'bg-blue-500/10 text-blue-400' : row.ghg_scope === 2 ? 'bg-purple-500/10 text-purple-400' : 'bg-indigo-500/10 text-indigo-400'
                        }`}>
                          Scope {row.ghg_scope}
                        </span>
                        {row.emission_activity_type}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono text-slate-300">
                        {parseFloat(row.normalized_quantity).toFixed(2)} <span className="text-xs text-slate-500">{row.normalized_unit}</span>
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono text-emerald-400 font-bold">
                        {parseFloat(row.calculated_carbon_footprint_kg).toFixed(2)} <span className="text-xs font-normal text-slate-500">kg</span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 text-xs">{row.accounting_date}</td>
                      
                      {/* Only render action button if we are looking at pending records */}
                      {currentTab === 'pending' && (
                        <td className="py-3.5 px-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button 
                              onClick={() => executeRowAction(row.id, 'APPROVE')}
                              className="bg-emerald-600/20 hover:bg-emerald-600 text-emerald-400 hover:text-white px-3 py-1.5 rounded text-xs font-semibold transition-all"
                            >
                              Approve
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}