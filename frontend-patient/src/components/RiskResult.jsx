import React from 'react';
import { AlertTriangle, CheckCircle, RefreshCcw, ShieldAlert, Activity, Ruler, HeartPulse, Zap, Info } from 'lucide-react';
import clsx from 'clsx';
import WellnessAshaPanel from './WellnessAshaPanel';
import WellnessWhatsAppPanel from './WellnessWhatsAppPanel';
import WellnessTriagePanel from './WellnessTriagePanel';
import WellnessChatAgent from './WellnessChatAgent';

export default function RiskResult({ assessment, onReset, isLowEnd, lang }) {
    const isDeviation = assessment.significant_deviation_detected;
    const score = assessment.neural_assessment_vector;

    return (
        <div className={clsx(
            "space-y-8",
            !isLowEnd && "animate-in fade-in slide-in-from-bottom-8 duration-700"
        )}>
            {/* Primary Analysis Card */}
            <div className={clsx(
                "glass-card p-8 border-b-8 text-center relative overflow-hidden",
                isDeviation ? "border-rose-600 bg-rose-500/5 shadow-[0_20px_50px_rgba(244,63,94,0.2)]" : "border-[#4ecdc4] bg-[#4ecdc4]/5 shadow-[0_20px_50px_rgba(78,205,196,0.1)]"
            )}>
                {/* Decorative Background Elements */}
                {!isLowEnd && (
                    <>
                        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-bl-full -mr-8 -mt-8 opacity-50" />
                        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-tr-full -ml-8 -mb-8 opacity-30" />
                    </>
                )}

                <div className="relative z-10 flex flex-col items-center">
                    <div className={clsx(
                        "w-24 h-24 rounded-3xl flex items-center justify-center mb-6 rotate-3 shadow-2xl relative neural-glow",
                        isDeviation ? "bg-rose-600 text-white shadow-rose-500/40" : "bg-[#4ecdc4] text-white shadow-[#4ecdc4]/40"
                    )}>
                        {isDeviation ? <ShieldAlert className="w-12 h-12" /> : <CheckCircle className="w-12 h-12" />}
                        {isDeviation && <div className="absolute -top-1 -right-1 w-4 h-4 bg-white rounded-full animate-ping" />}
                    </div>

                    <p className="text-[10px] font-black tracking-[0.3em] text-white/40 mb-2 uppercase">Neural Assessment Vector</p>
                    <h2 className={clsx("text-4xl font-black mb-4 tracking-tighter italic", isDeviation ? "text-white glow-red" : "text-[#4ecdc4] glow-cyan")}>
                        {isDeviation ? (lang === 'hi' ? "पैटर्न विचलन" : "PATTERN DEVIATION") : (lang === 'hi' ? "बेसलाइन स्थिर" : "BASELINE STABLE")}
                    </h2>

                    <div className="relative mb-8 group">
                        <div className={clsx(
                            "text-9xl font-black tracking-tighter text-white opacity-90 transition-transform duration-500",
                            isDeviation ? "glow-red" : "glow-cyan"
                        )}>
                            {score}
                        </div>
                        <div className="absolute -right-12 bottom-6 text-xs font-black text-white/20 uppercase tracking-[0.5em] rotate-90 origin-bottom-left">
                            WELLNESS INDEX
                        </div>
                    </div>

                    <div className={clsx(
                        "text-[10px] sm:text-xs font-black py-4 px-6 rounded-2xl mb-1 flex items-center gap-3 border shadow-2xl backdrop-blur-md italic tracking-widest uppercase text-left leading-relaxed",
                        isDeviation ? "bg-rose-600 text-white border-rose-400/50" : "bg-[#4ecdc4] text-white border-[#4ecdc4]/50"
                    )}>
                       <Zap className="w-5 h-5 shrink-0 animate-pulse fill-current" /> {assessment.wellness_suggestion}
                    </div>
                </div>
            </div>

            {/* India-Specific Wellness Support Panels */}
            {isDeviation && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <WellnessAshaPanel lang={lang} />
                    <WellnessWhatsAppPanel lang={lang} />
                    <WellnessTriagePanel lang={lang} currentLevel="emergency" />
                </div>
            )}

            {/* AI Assistant Agent */}
            <WellnessChatAgent lang={lang} isDeviation={isDeviation} />

            {/* Observation Details */}
            {assessment.significant_observations.length > 0 && (
                <div className="space-y-4 text-left">
                    <h3 className="text-[10px] font-black text-white/30 uppercase mb-4 tracking-[0.4em] flex items-center gap-2">
                        <Activity className="w-3 h-3 text-[#4ecdc4]" /> Neural Pattern Observations
                    </h3>
                    <div className="space-y-3">
                        {assessment.significant_observations.map((obs, idx) => (
                            <div key={idx} className="glass-card p-5 border-white/5 bg-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex justify-between items-center mb-3">
                                    <span className="font-black text-[10px] text-white uppercase tracking-tight italic w-[70%]">{obs.pattern_name}</span>
                                    <span className={clsx(
                                        "font-black text-xl tracking-tighter",
                                        obs.assessment_index > 0.8 ? "text-rose-500" : "text-[#4ecdc4]"
                                    )}>
                                        {(obs.assessment_index * 100).toFixed(0)}%
                                    </span>
                                </div>
                                <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden mb-4">
                                    <div className={clsx(
                                        "h-full rounded-full transition-all duration-1000",
                                        obs.assessment_index > 0.8 ? "bg-rose-600" : "bg-[#4ecdc4]"
                                    )} style={{ width: `${obs.assessment_index * 100}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <button
                onClick={onReset}
                className="w-full bg-white hover:bg-white/90 active:scale-95 text-[#0a0e27] font-black py-6 rounded-3xl shadow-[0_20px_50px_rgba(255,255,255,0.1)] flex items-center justify-center gap-4 transition-all duration-300 group"
            >
                <RefreshCcw className="w-6 h-6 group-hover:rotate-180 transition-transform duration-700" /> 
                <span className="tracking-[0.3em] uppercase text-sm">{lang === 'hi' ? "नया स्कैन शुरू करें" : "Initiate New Scan Loop"}</span>
            </button>
        </div>
    );
}
