import React, { useState, useRef, useEffect } from 'react';
import { Shield, Activity, Settings, Download, Users, AlertTriangle } from 'lucide-react';
import Webcam from 'react-webcam';
import { motion } from 'framer-motion';
import { AnimatePresence } from 'framer-motion';
// Mock data structure
const MOCK_LOGS = [
  { id: 1, name: 'John Anderson', timestamp: new Date().toISOString(), status: 'authorized' },
  { id: 2, name: 'Sarah Chen', timestamp: new Date(Date.now() - 120000).toISOString(), status: 'authorized' },
  { id: 3, name: 'Mahalaxmi', timestamp: new Date(Date.now() - 240000).toISOString(), status: 'unauthorized' },
  { id: 4, name: 'Mike Roberts', timestamp: new Date(Date.now() - 360000).toISOString(), status: 'authorized' },
  { id: 5, name: 'Unknown Person', timestamp: new Date(Date.now() - 480000).toISOString(), status: 'unauthorized' },
  { id: 6, name: 'Emily Watson', timestamp: new Date(Date.now() - 600000).toISOString(), status: 'authorized' },
  { id: 7, name: 'David Kim', timestamp: new Date(Date.now() - 720000).toISOString(), status: 'authorized' },
  { id: 8, name: 'Unauthorized Access', timestamp: new Date(Date.now() - 840000).toISOString(), status: 'unauthorized' },
  { id: 9, name: 'Jessica Martinez', timestamp: new Date(Date.now() - 960000).toISOString(), status: 'authorized' },
  { id: 10, name: 'Robert Taylor', timestamp: new Date(Date.now() - 1080000).toISOString(), status: 'authorized' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [countdown, setCountdown] = useState(3);
  const [enrollProgress, setEnrollProgress] = useState(0);
  const [logs, setLogs] = useState(MOCK_LOGS);
  const webcamRef = useRef(null);

  // Countdown and enrollment logic
  useEffect(() => {
    if (isEnrolling && countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (isEnrolling && countdown === 0) {
      // Start progress bar
      const progressTimer = setInterval(() => {
        setEnrollProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressTimer);
            setTimeout(() => {
              setIsEnrolling(false);
              setCountdown(3);
              setEnrollProgress(0);
            }, 500);
            return 100;
          }
          return prev + 5;
        });
      }, 75);
      return () => clearInterval(progressTimer);
    }
  }, [isEnrolling, countdown]);

  const handleDownload = (filterType: string) => {
    let filteredLogs = logs;
    let filename = 'arani_logs_all.csv';

    switch (filterType) {
      case 'authorized':
        filteredLogs = logs.filter(log => log.status === 'authorized');
        filename = 'arani_logs_authorized.csv';
        break;
      case 'breaches':
        filteredLogs = logs.filter(log => log.status === 'unauthorized');
        filename = 'arani_logs_breaches.csv';
        break;
      default:
        break;
    }

    // Convert to CSV
    const headers = 'ID,Name,Timestamp,Status\n';
    const csvContent = filteredLogs.map(log => 
      `${log.id},"${log.name}","${new Date(log.timestamp).toLocaleString()}","${log.status}"`
    ).join('\n');
    
    const csv = headers + csvContent;
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setShowDownloadMenu(false);
  };

  const startEnrollment = () => {
    setIsEnrolling(true);
    setCountdown(3);
    setEnrollProgress(0);
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-black text-gray-100 flex">
      {/* Left Sidebar */}
      <div className="w-20 bg-zinc-900 border-r border-zinc-800 flex flex-col items-center py-6 space-y-8">
        <div className="text-green-500 font-bold text-xl mb-4">A2.0</div>
        
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`p-3 rounded-lg transition-all ${
            activeTab === 'dashboard' ? 'bg-green-500/20 text-green-500' : 'text-gray-400 hover:text-green-500'
          }`}
        >
          <Shield size={24} />
        </button>
        
        <button
          onClick={() => setActiveTab('activity')}
          className={`p-3 rounded-lg transition-all ${
            activeTab === 'activity' ? 'bg-green-500/20 text-green-500' : 'text-gray-400 hover:text-green-500'
          }`}
        >
          <Activity size={24} />
        </button>

        <div className="relative">
          <button
            onClick={() => setShowDownloadMenu(!showDownloadMenu)}
            className="p-3 rounded-lg text-gray-400 hover:text-green-500 transition-all"
          >
            <Download size={24} />
          </button>
          
          <AnimatePresence>
            {showDownloadMenu && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="absolute left-full ml-2 top-0 bg-zinc-800 border border-zinc-700 rounded-lg shadow-xl w-48 overflow-hidden z-50"
              >
                <button
                  onClick={() => handleDownload('all')}
                  className="w-full px-4 py-3 text-left text-sm hover:bg-zinc-700 transition-colors"
                >
                  Export All
                </button>
                <button
                  onClick={() => handleDownload('authorized')}
                  className="w-full px-4 py-3 text-left text-sm hover:bg-zinc-700 transition-colors border-t border-zinc-700"
                >
                  Authorized Only
                </button>
                <button
                  onClick={() => handleDownload('breaches')}
                  className="w-full px-4 py-3 text-left text-sm hover:bg-zinc-700 transition-colors border-t border-zinc-700"
                >
                  Security Breaches
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button
          onClick={() => setActiveTab('settings')}
          className={`p-3 rounded-lg transition-all ${
            activeTab === 'settings' ? 'bg-green-500/20 text-green-500' : 'text-gray-400 hover:text-green-500'
          }`}
        >
          <Settings size={24} />
        </button>
      </div>

      {/* Center Panel - Webcam Feed */}
      <div className="flex-1 p-6 flex flex-col">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-green-500">ARANI 2.0</h1>
          <p className="text-gray-400 text-sm">Tactical AI Security System</p>
        </div>

        <div className="flex-1 bg-zinc-900 rounded-lg border border-zinc-800 relative overflow-hidden">
          <Webcam
            ref={webcamRef}
            audio={false}
            className="w-full h-full object-cover"
            screenshotFormat="image/jpeg"
          />

          {/* Scanning Overlay */}
          <div className="absolute inset-0 pointer-events-none">
            {/* Corner Markers */}
            <motion.div
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute top-8 left-8 w-16 h-16 border-t-4 border-l-4 border-green-500"
            />
            <motion.div
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
              className="absolute top-8 right-8 w-16 h-16 border-t-4 border-r-4 border-green-500"
            />
            <motion.div
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity, delay: 1 }}
              className="absolute bottom-8 left-8 w-16 h-16 border-b-4 border-l-4 border-green-500"
            />
            <motion.div
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity, delay: 1.5 }}
              className="absolute bottom-8 right-8 w-16 h-16 border-b-4 border-r-4 border-green-500"
            />

            {/* Targeting Reticle */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="relative w-32 h-32">
                <div className="absolute inset-0 border-2 border-green-500 rounded-full opacity-30" />
                <div className="absolute inset-4 border-2 border-green-500 rounded-full opacity-50" />
                <div className="absolute inset-8 border-2 border-green-500 rounded-full opacity-70" />
                <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-green-500 opacity-50" />
                <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-green-500 opacity-50" />
              </div>
            </div>

            {/* Scan Line */}
            <motion.div
              animate={{ top: ['0%', '100%'] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
              className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-green-500 to-transparent opacity-30"
            />
          </div>

          {/* Enrollment Countdown Overlay */}
          <AnimatePresence>
            {isEnrolling && countdown > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/70 flex items-center justify-center"
              >
                <motion.div
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  className="text-9xl font-bold text-green-500"
                >
                  {countdown}
                </motion.div>
              </motion.div>
            )}

            {isEnrolling && countdown === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute inset-0 bg-black/70 flex items-center justify-center"
              >
                <div className="w-96 space-y-4">
                  <div className="text-2xl font-bold text-green-500 text-center">
                    Capturing Face Data...
                  </div>
                  <div className="w-full bg-zinc-800 rounded-full h-4 overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-green-600 to-green-400"
                      style={{ width: `${enrollProgress}%` }}
                    />
                  </div>
                  <div className="text-center text-green-500 text-sm">
                    {enrollProgress}%
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Control Buttons */}
        <div className="mt-4 flex gap-4">
          <button
            onClick={startEnrollment}
            disabled={isEnrolling}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
          >
            <Users size={20} />
            Start Face Enrollment
          </button>
        </div>
      </div>

      {/* Right Sidebar - Live Intel Feed */}
      <div className="w-80 bg-zinc-900 border-l border-zinc-800 p-6 flex flex-col">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-green-500 mb-1">Live Intel Feed</h2>
          <p className="text-xs text-gray-400">Real-time detection logs</p>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 pr-2">
          {logs.map((log, index) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`p-4 rounded-lg border ${
                log.status === 'authorized'
                  ? 'bg-green-500/10 border-green-500/30'
                  : 'bg-red-500/10 border-red-500/30'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="font-semibold text-sm">{log.name}</div>
                {log.status === 'unauthorized' && (
                  <AlertTriangle size={16} className="text-red-500 flex-shrink-0" />
                )}
              </div>
              
              <div className="text-xs text-gray-400 mb-2">
                {formatTime(log.timestamp)}
              </div>
              
              <div className={`text-xs font-semibold uppercase ${
                log.status === 'authorized' ? 'text-green-500' : 'text-red-500'
              }`}>
                {log.status}
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-zinc-800">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Total Scans:</span>
            <span className="text-green-500 font-bold">{logs.length}</span>
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-2">
            <span>Breaches:</span>
            <span className="text-red-500 font-bold">
              {logs.filter(l => l.status === 'unauthorized').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}