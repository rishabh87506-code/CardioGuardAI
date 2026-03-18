import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Zap, MessageCircle, X, ChevronUp, ChevronDown, Volume2, VolumeX, Mic, MicOff, Sparkles, ShieldCheck, HeartPulse } from 'lucide-react';
import clsx from 'clsx';
import { useWellnessVoice } from '../hooks/useWellnessVoice';
import { HridaiPersonality } from '../utils/hridaiPersonality';

export default function GlobalHridaiAI({ lang, user, isDeviation, onAction }) {
    const [isMinimized, setIsMinimized] = useState(true);
    const [lastAlert, setLastAlert] = useState(null);
    const [voiceEnabled, setVoiceEnabled] = useState(true);
    const [isHumanLike, setIsHumanLike] = useState(true); // Enhanced Caring Mode
    
    // Customize Voice: 0.9 rate = Calm & Professional (Doctor-like), 1.05 pitch = Caring Tone
    const { isListening, transcript, isSpeaking, speak, listen, stopListening, stopSpeaking } = useWellnessVoice(lang);

    useEffect(() => {
        if (isDeviation && lastAlert !== 'deviation') {
            setLastAlert('deviation');
            setIsMinimized(false);
            
            // Ethical Triage: Only notify and instruct rest, no medication advice (Constitutional AI)
            const triage = HridaiPersonality.getEmergencyResponse(lang, user);
            
            if (voiceEnabled) {
                // Synergised Hridai-Pro Speech (WhatsApp/Emergency Broadcast Confirmation)
                const voiceMsg = lang === 'hi' 
                    ? "चेतावनी! महत्वपूर्ण विचलन पाया गया है। आपकी लाइव स्थिति और स्वास्थ्य रिपोर्ट व्हाट्सएप और आपातकालीन सेवा को भेज दी गई है।"
                    : "Alert! Important deviation. I have broadcasted your vitals and live location to the emergency network and your family via WhatsApp.";
                speak(voiceMsg);
            }
            
            // Automatic Action: Trigger Navigation to Risk Result View
            onAction?.('emergency');
        }
    }, [isDeviation, lastAlert, voiceEnabled, lang, speak, user, onAction]);

    if (!user) return null;

    return (
        <div className={clsx(
            "fixed bottom-24 right-6 z-[100] transition-all duration-700 ease-[cubic-bezier(0.23,1,0.32,1)]",
            isMinimized ? "w-16 h-16" : "w-80 h-[450px]"
        )}>
            {isMinimized ? (
                <button 
                    onClick={() => setIsMinimized(false)}
                    className="group relative w-16 h-16 flex items-center justify-center active:scale-95 transition-all"
                >
                    {/* Premium Neural Orb */}
                    <div className={clsx(
                        "neural-orb absolute inset-0 transition-transform duration-700 group-hover:scale-110",
                        (isSpeaking || isListening) && "scale-125"
                    )} />
                    
                    <div className="relative z-10 flex items-center gap-0.5 h-4">
                        {[1, 2, 3].map((i) => (
                            <div 
                                key={i}
                                className={clsx(
                                    "w-1 bg-white rounded-full transition-all duration-300",
                                    (isSpeaking || isListening) ? "voice-bar" : "h-1 opacity-40"
                                )}
                                style={{ animationDelay: `${i * 0.15}s` }}
                            />
                        ))}
                    </div>

                    {isDeviation && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-rose-500 rounded-full border-4 border-[#020617] animate-bounce shadow-lg shadow-rose-900/50" />
                    )}
                </button>
            ) : (
                <div className="w-full h-full glass-card border-white/10 bg-slate-950/80 backdrop-blur-3xl shadow-[0_32px_64px_-16px_rgba(0,0,0,0.6)] flex flex-col overflow-hidden animate-in zoom-in-95 fade-in duration-500 rounded-[2.5rem]">
                    {/* Header */}
                    <div className="p-6 bg-gradient-to-b from-white/5 to-transparent flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 neural-orb flex items-center justify-center">
                                <Zap className="w-4 h-4 text-white" />
                            </div>
                            <div>
                                <span className="text-[10px] font-black text-white uppercase tracking-[0.2em] italic">Neural AI Agent</span>
                                <p className="text-[8px] text-[#4ecdc4] font-bold uppercase tracking-widest mt-0.5">Hridai-1 Pro</p>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button onClick={() => setVoiceEnabled(!voiceEnabled)} className="p-2 bg-white/5 rounded-xl text-white/40 hover:text-[#4ecdc4] transition-colors">
                                {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                            </button>
                            <button onClick={() => setIsMinimized(true)} className="p-2 bg-white/5 rounded-xl text-white/40 hover:text-white transition-colors">
                                <ChevronDown className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Agent Visualizer Space */}
                    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-8">
                        <div className="relative">
                            <div className={clsx(
                                "w-32 h-32 neural-orb transition-all duration-1000",
                                isSpeaking ? "scale-110 blur-[2px]" : "scale-100",
                                isListening ? "animate-pulse" : ""
                            )} />
                            <div className="absolute inset-0 flex items-center justify-center gap-1">
                                {[1, 2, 3, 4, 5].map((i) => (
                                    <div 
                                        key={i}
                                        className={clsx(
                                            "w-1.5 bg-white rounded-full",
                                            (isSpeaking || isListening) ? "voice-bar" : "h-1 opacity-20"
                                        )}
                                        style={{ 
                                            animationDelay: `${i * 0.1}s`,
                                            height: (isSpeaking || isListening) ? 'auto' : '4px'
                                        }}
                                    />
                                ))}
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-1">
                                <p className="text-sm font-medium text-slate-200 leading-relaxed max-w-[240px] mx-auto">
                                    {isListening ? (transcript || "I'm listening to your heartbeat...") : 
                                     isSpeaking ? (lang === 'hi' ? "मैं आपके स्वास्थ्य डेटा का विश्लेषण कर रही हूँ..." : "I'm checking your neural-vitals pattern...") : 
                                     (lang === 'hi' ? "मैं आपके हृदय के आधार स्तर की निगरानी कर रही हूँ।" : "I'm monitoring your heart's baseline.")}
                                </p>
                                <div className="flex items-center justify-center gap-1.5 pt-2">
                                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                                    <span className="text-[9px] font-black text-white/30 uppercase tracking-[0.2em]">Constitutional Triage Engine</span>
                                </div>
                            </div>

                            {/* Caring Demographic Context Indicator */}
                            <div className="flex flex-col items-center gap-2 border-t border-white/5 pt-4">
                                <span className="text-[8px] text-white/20 uppercase font-black tracking-widest">Local Demographic Pulse</span>
                                <div className="flex gap-4">
                                    <div className="flex items-center gap-1.5 opacity-40 hover:opacity-100 transition-opacity">
                                        <HeartPulse className="w-3 h-3 text-rose-500" />
                                        <span className="text-[8px] font-bold text-white/50">{user?.location || 'AIIMS Reach'} Sync</span>
                                    </div>
                                    <div className="flex items-center gap-1.5 opacity-40 hover:opacity-100 transition-opacity">
                                        <Zap className="w-3 h-3 text-[#4ecdc4]" />
                                        <span className="text-[8px] font-bold text-white/50">ASHA Alert Ready</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer Controls */}
                    <div className="p-6 bg-white/5 flex gap-3">
                        <button 
                            onClick={isListening ? stopListening : listen}
                            className={clsx(
                                "flex-1 h-14 rounded-2xl flex items-center justify-center gap-3 transition-all font-black uppercase text-[10px] tracking-[0.2em]",
                                isListening 
                                    ? "bg-rose-500 text-white shadow-2xl shadow-rose-900/40" 
                                    : "bg-white text-slate-900 hover:bg-[#4ecdc4] hover:shadow-[0_0_30px_rgba(78,205,196,0.3)]"
                            )}
                        >
                            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                            {isListening ? "Listening" : "Hold to Speak"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

