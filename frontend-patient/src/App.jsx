import React, { useState, useEffect } from 'react';
import { Heart, Activity, History, ClipboardCheck, Globe, Info, MessageCircle, AlertCircle } from 'lucide-react';
import VitalsForm from './components/VitalsForm';
import RiskResult from './components/RiskResult';
import HistoryView from './components/HistoryView';

function App() {
    const [currentView, setCurrentView] = useState('input'); // 'input' | 'result' | 'history'
    const [assessment, setAssessment] = useState(null);
    const [lang, setLang] = useState('en');
    const [offline, setOffline] = useState(!navigator.onLine);
    const [isLowEnd, setIsLowEnd] = useState(false);

    useEffect(() => {
        // Device Detection
        const lowEnd = (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2) || 
                       (navigator.deviceMemory && navigator.deviceMemory <= 2);
        setIsLowEnd(!!lowEnd);
        
        if (lowEnd) {
            document.body.classList.add('low-perf');
        }

        const handleOnline = () => setOffline(false);
        const handleOffline = () => setOffline(true);
        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);
        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    const handleAssessmentComplete = (data) => {
        setAssessment(data);
        setCurrentView('result');
    };

    const resetFlow = () => {
        setAssessment(null);
        setCurrentView('input');
    };

    const strings = {
        en: {
            title: "CardioGuard AI",
            subtitle: "भारत संस्करण | Indian Edition",
            badge: "🇮🇳 Wellness Platform",
            monitoring: "Monitoring",
            checkup: "Checkup",
            history: "History",
            disclaimer: "ℹ️ This is a wellness platform. For medical concerns, consult healthcare professionals."
        },
        hi: {
            title: "CardioGuard AI",
            subtitle: "भारत संस्करण | स्वास्थ्य मंच",
            badge: "🇮🇳 कल्याण मंच",
            monitoring: "निगरानी",
            checkup: "जाँच",
            history: "इतिहास",
            disclaimer: "ℹ️ यह एक कल्याण मंच है। चिकित्सा संबंधी चिंताओं के लिए पेशेवरों से परामर्श लें।"
        }
    };

    return (
        <div className="min-h-screen pb-24">
            {/* Offline Indicator */}
            {offline && (
                <div className="bg-rose-500 text-white text-center py-2 text-xs font-bold animate-pulse fixed top-0 w-full z-50">
                    📴 Operating in Offline Mode
                </div>
            )}

            {/* Header */}
            <header className="sticky top-0 z-40 bg-[#0a0e27]/80 backdrop-blur-xl border-b border-white/5 px-4 py-3">
                <div className="max-w-md mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="logo-icon overflow-hidden">
                            <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
                        </div>
                        <div>
                            <h1 className="logo-text text-xl font-black italic tracking-tighter uppercase leading-none">
                                CardioGuard <span className="text-white">AI</span>
                            </h1>
                            <p className="text-[10px] text-white/50 font-bold uppercase tracking-widest mt-0.5">
                                {strings[lang].subtitle}
                            </p>
                            {isLowEnd && (
                                <span className="bg-amber-500/20 text-amber-500 text-[8px] font-black px-1.5 py-0.5 rounded leading-none inline-block mt-0.5 uppercase">
                                    Lite Mode
                                </span>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <button 
                            onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
                            className="bg-white/5 hover:bg-white/10 p-2 rounded-full border border-white/10 transition-all active:scale-90"
                        >
                            <Globe className="w-4 h-4 text-[#4ecdc4]" />
                        </button>
                        <div className="flex items-center gap-2 bg-[#4ecdc4]/10 border border-[#4ecdc4]/30 px-3 py-1.5 rounded-full">
                            <div className="status-dot"></div>
                            <span className="text-[10px] font-black text-[#4ecdc4] uppercase tracking-wider">
                                {strings[lang].monitoring}
                            </span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-md mx-auto p-5 space-y-4">
                {/* Global Wellness Banner */}
                <div className="glass-card p-4 border-[#4ecdc4]/20 bg-[#4ecdc4]/5">
                    <div className="flex gap-3">
                        <Info className="w-5 h-5 text-[#4ecdc4] shrink-0" />
                        <p className="text-xs leading-relaxed text-white/70">
                            {strings[lang].disclaimer}
                        </p>
                    </div>
                </div>

                {currentView === 'input' && <VitalsForm onComplete={handleAssessmentComplete} isLowEnd={isLowEnd} />}
                {currentView === 'result' && assessment && <RiskResult assessment={assessment} onReset={resetFlow} isLowEnd={isLowEnd} lang={lang} />}
                {currentView === 'history' && <HistoryView isLowEnd={isLowEnd} />}
            </main>

            {/* Bottom Nav */}
            <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[92%] max-w-md bg-white/5 backdrop-blur-2xl border border-white/10 p-2 rounded-3xl shadow-2xl flex justify-around items-center z-50">
                <button 
                    onClick={() => setCurrentView('input')}
                    className={`flex flex-col items-center gap-1 py-2 px-5 rounded-2xl transition-all ${currentView === 'input' || currentView === 'result' ? 'bg-[#ff6b6b] text-white shadow-[0_0_20px_rgba(255,107,107,0.4)]' : 'text-white/40 hover:text-white/70'}`}
                >
                    <ClipboardCheck className="w-5 h-5" />
                    <span className="text-[10px] font-black uppercase tracking-widest">{strings[lang].checkup}</span>
                </button>
                <button 
                    onClick={() => setCurrentView('history')}
                    className={`flex flex-col items-center gap-1 py-2 px-5 rounded-2xl transition-all ${currentView === 'history' ? 'bg-[#ff6b6b] text-white shadow-[0_0_20px_rgba(255,107,107,0.4)]' : 'text-white/40 hover:text-white/70'}`}
                >
                    <History className="w-5 h-5" />
                    <span className="text-[10px] font-black uppercase tracking-widest">{strings[lang].history}</span>
                </button>
            </nav>

            <footer className="max-w-md mx-auto p-8 pt-4 text-center">
                <div className="india-badge inline-block mb-2">भारत संस्करण</div>
                <p className="text-[10px] text-white/30 font-black tracking-widest uppercase">
                    © 2026 CardioGuard AI Systems • NEURAL PULSE ENGINE
                </p>
            </footer>
        </div>
    );
}

export default App;
