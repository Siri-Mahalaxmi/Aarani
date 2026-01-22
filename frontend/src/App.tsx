import React, { useState, useRef, useEffect } from 'react';
import { Shield, Activity, Download, ShieldAlert } from 'lucide-react';
import Webcam from 'react-webcam';
import { motion, AnimatePresence } from 'framer-motion';

// Interface for the logs coming from Python
interface DetectionLog {
  id: number;
  name: string;
  timestamp: string;
  status: 'authorized' | 'unauthorized';
}

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [cameraEnabled, setCameraEnabled] = useState(true); // Manages camera hardware
  const [countdown, setCountdown] = useState(3);
  const [enrollProgress, setEnrollProgress] = useState(0);
  const [logs, setLogs] = useState<DetectionLog[]>([]); 
  const webcamRef = useRef<Webcam>(null);

  // 1. REAL-TIME DATA POLLING: Connects to Python app.py
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/logs');
        if (response.ok) {
          const data = await response.json();
          setLogs(data); // Updates the sidebar with real AI detections
        }
      } catch (err) {
        console.log("Waiting for Python Bridge...");
      }
    };

    const interval = setInterval(fetchLogs, 1500); // Poll frequently for live demo
    return () => clearInterval(interval);
  }, []);

  // 2. ENROLLMENT TRIGGER: Connects to Python Flask Route
  const startEnrollment = async () => {
    const personName = prompt("Enter Name for Enrollment:");
    if (!personName) return;

    // STEP A: Release camera so Python can grab it
    setCameraEnabled(false); 
    setIsEnrolling(true);
    setCountdown(3);
    setEnrollProgress(0);

    try {
      // Give the hardware 1 second to fully release
      await new Promise(resolve => setTimeout(resolve, 1000));

      const response = await fetch('http://localhost:5000/api/enroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: personName }) // Sends the name to app.py
      });

      if (!response.ok) throw new Error("Enrollment script failed");
      
      alert(`Enrollment for ${personName} successful!`);
    } catch (err) {
      alert("Error: Ensure Python app.py is running and camera is available.");
    } finally {
      setIsEnrolling(false);
      setCameraEnabled(true); // STEP B: Re-enable dashboard camera
    }
  };

  // Enrollment Visual Logic (UI Only)
  useEffect(() => {
    if (isEnrolling && countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (isEnrolling && countdown === 0) {
      const progressTimer = setInterval(() => {
        setEnrollProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressTimer);
            return 100;
          }
          return prev + 2;
        });
      }, 50);
      return () => clearInterval(progressTimer);
    }
  }, [isEnrolling, countdown]);

  const handleDownload = (filterType: string) => {
    let filteredLogs = logs;
    if (filterType === 'authorized') filteredLogs = logs.filter(l => l.status === 'authorized');
    if (filterType === 'breaches') filteredLogs = logs.filter(l => l.status === 'unauthorized');

    const headers = 'Name,Timestamp,Status\n';
    const csvContent = filteredLogs.map(log => `"${log.name}","${log.timestamp}","${log.status}"`).join('\n');
    const blob = new Blob([headers + csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `arani_report_${filterType}.csv`;
    link.click();
  };

  return (
    <div className="min-h-screen bg-[#0D0D0D] text-gray-100 flex font-mono overflow-hidden">
      {/* Sidebar */}
      <div className="w-20 bg-[#1A1A1A] border-r border-zinc-800 flex flex-col items-center py-6 space-y-8">
        <div className="text-[#00FF85] font-bold text-xl mb-4 tracking-tighter">A2.0</div>
        <button onClick={() => setActiveTab('dashboard')} className={`p-3 rounded-lg ${activeTab === 'dashboard' ? 'text-[#00FF85] bg-[#00FF85]/10' : 'text-zinc-500'}`}><Shield size={24} /></button>
        <button onClick={() => setActiveTab('activity')} className={`p-3 rounded-lg ${activeTab === 'activity' ? 'text-[#00FF85] bg-[#00FF85]/10' : 'text-zinc-500'}`}><Activity size={24} /></button>
        <button onClick={() => setShowDownloadMenu(!showDownloadMenu)} className="p-3 text-zinc-500 hover:text-[#00FF85]"><Download size={24} /></button>
      </div>

      {/* Main View */}
      <div className="flex-1 p-8 flex flex-col">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-4xl font-black text-[#00FF85] tracking-tight italic">ARANI 2.0</h1>
            <p className="text-zinc-500 text-xs uppercase tracking-[0.3em]">Advanced Biometric Security</p>
          </div>
          <div className="text-right">
            <div className="text-[#00FF85] text-xs font-bold animate-pulse">● BIOMETRIC NODE ACTIVE</div>
            <div className="text-zinc-500 text-[10px]">HOST: 127.0.0.1:5000</div>
          </div>
        </div>

        <div className="flex-1 bg-[#121212] rounded-3xl border border-zinc-800 relative overflow-hidden shadow-[0_0_50px_rgba(0,255,133,0.05)]">
          {/* CAMERA FEED LOGIC */}
          {cameraEnabled ? (
            <Webcam ref={webcamRef} audio={false} className="w-full h-full object-cover opacity-80" />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center bg-black">
               <ShieldAlert size={48} className="text-[#00FF85] animate-bounce mb-4" />
               <p className="text-[#00FF85] text-xs tracking-widest uppercase">Releasing Hardware for AI Enrollment</p>
            </div>
          )}
          
          {/* Scanning HUD Overlay */}
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-10 left-10 w-16 h-16 border-t-2 border-l-2 border-[#00FF85]/40" />
            <div className="absolute top-10 right-10 w-16 h-16 border-t-2 border-r-2 border-[#00FF85]/40" />
            <div className="absolute bottom-10 left-10 w-16 h-16 border-b-2 border-l-2 border-[#00FF85]/40" />
            <div className="absolute bottom-10 right-10 w-16 h-16 border-b-2 border-r-2 border-[#00FF85]/40" />
          </div>

          <AnimatePresence>
            {isEnrolling && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="absolute inset-0 bg-black/90 flex items-center justify-center z-50">
                <div className="text-center">
                  <div className="text-8xl font-black text-[#00FF85] mb-2">{countdown > 0 ? countdown : `${enrollProgress}%`}</div>
                  <div className="text-[#00FF85] tracking-[0.5em] uppercase text-xs">Biometric Extraction in Progress</div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button onClick={startEnrollment} disabled={isEnrolling} className="mt-8 w-full bg-[#00FF85] text-black font-black py-5 rounded-2xl hover:bg-[#00cc6a] disabled:bg-zinc-900 disabled:text-zinc-700 transition-all uppercase tracking-widest text-sm">
          {isEnrolling ? 'Processing...' : 'Register New Biometric Subject'}
        </button>
      </div>

      {/* Intel Feed Sidebar */}
      <div className="w-96 bg-[#121212] border-l border-zinc-800 p-8 flex flex-col">
        <h2 className="text-[#00FF85] font-black text-xl mb-6 flex items-center gap-2">
          <Activity size={20} /> LIVE INTEL
        </h2>

        <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
          {logs.length === 0 ? (
            <div className="text-zinc-700 text-xs text-center mt-20 italic">Scanning for authorized signatures...</div>
          ) : (
            logs.map((log) => (
              <motion.div key={log.id} initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className={`p-4 rounded-xl border-l-4 ${log.status === 'authorized' ? 'border-[#00FF85] bg-[#00FF85]/5' : 'border-[#FF3E3E] bg-[#FF3E3E]/5'}`}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-bold tracking-tighter">{log.name}</span>
                  <span className="text-[9px] text-zinc-500">{log.timestamp}</span>
                </div>
                <div className={`text-[9px] font-black tracking-widest uppercase ${log.status === 'authorized' ? 'text-[#00FF85]' : 'text-[#FF3E3E]'}`}>
                  {log.status}
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}