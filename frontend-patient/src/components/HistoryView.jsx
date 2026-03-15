import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Clock, TrendingUp, AlertCircle, Loader2, Calendar, Activity, Gauge } from 'lucide-react';

const HISTORY_URL = "http://localhost:8000/api/v1/vitals/history";

export default function HistoryView() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await axios.get(HISTORY_URL);
                setHistory(response.data);
            } catch (err) {
                console.error("Error fetching history:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-in fade-in duration-1000">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-white/5 border-t-[#ff6b6b] rounded-full animate-spin" />
                    <HeartPulse className="w-6 h-6 text-[#ff6b6b] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                </div>
                <p className="mt-4 text-white/40 text-[10px] font-black uppercase tracking-[0.3em]">Synching Neural History</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between mb-2">
                <div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tight italic">
                        Wellness <span className="text-[#4ecdc4]">Timeline</span>
                    </h2>
                    <p className="text-white/40 text-[10px] font-bold uppercase tracking-widest mt-1">
                        Historical neural assessment log
                    </p>
                </div>
                <div className="bg-[#4ecdc4]/10 border border-[#4ecdc4]/30 text-[#4ecdc4] px-4 py-2 rounded-2xl text-[10px] font-black uppercase">
                    {history.length} Logs
                </div>
            </div>

            {history.length === 0 ? (
                <div className="glass-card p-12 text-center border-dashed border-white/10">
                    <Clock className="w-12 h-12 text-white/10 mx-auto mb-4" />
                    <p className="text-white/40 text-[10px] font-black uppercase tracking-[0.2em]">Zero Data Points Detected</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {history.slice().reverse().map((record, idx) => (
                        <div key={idx} className="glass-card p-5 border-white/10 transition-all hover:bg-white/5 group">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-2">
                                    <Calendar className="w-3 h-3 text-white/30" />
                                    <span className="text-[10px] font-black text-white/30 uppercase tracking-widest">
                                        {new Date(record.timestamp || Date.now()).toLocaleDateString('en-IN', {
                                            day: 'numeric',
                                            month: 'short',
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                    </span>
                                </div>
                                {record.hr > 120 && (
                                    <div className="bg-rose-500/10 text-rose-500 border border-rose-500/30 px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest animate-pulse">
                                        High Stress
                                    </div>
                                )}
                            </div>
                            
                            <div className="grid grid-cols-3 gap-3">
                                <div className="bg-white/5 rounded-2xl p-3 border border-white/5 group-hover:border-[#ff6b6b]/30">
                                    <p className="text-[8px] font-black text-white/30 uppercase mb-1 flex items-center gap-1">
                                        <Activity className="w-2.5 h-2.5" /> Pulse
                                    </p>
                                    <p className="text-xl font-black text-[#ff6b6b] tracking-tighter">{record.hr}<span className="text-[10px] ml-1 opacity-50">BMP</span></p>
                                </div>
                                <div className="bg-white/5 rounded-2xl p-3 border border-white/5 group-hover:border-[#4ecdc4]/30">
                                    <p className="text-[8px] font-black text-white/30 uppercase mb-1 flex items-center gap-1">
                                        <Gauge className="w-2.5 h-2.5" /> Pressure
                                    </p>
                                    <p className="text-xl font-black text-white tracking-tighter">{record.sbp}<span className="mx-0.5 opacity-20">/</span>{record.dbp}</p>
                                </div>
                                <div className="bg-white/5 rounded-2xl p-3 border border-white/5 group-hover:border-white/20">
                                    <p className="text-[8px] font-black text-white/30 uppercase mb-1 flex items-center gap-1">
                                        <TrendingUp className="w-2.5 h-2.5" /> BMI
                                    </p>
                                    <p className="text-xl font-black text-[#4ecdc4] tracking-tighter">{record.meta_bmi || record.bmi}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

// Sub-component Helper
const HeartPulse = ({ className }) => (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
    </svg>
);
