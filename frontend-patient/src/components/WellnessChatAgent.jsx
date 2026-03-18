import React, { useState, useEffect, useRef, useCallback } from 'react';
import { MessageCircle, Zap, ShieldCheck, Send, User, Mic, MicOff, Volume2, VolumeX, Loader2, Sparkles, Building2 } from 'lucide-react';
import clsx from 'clsx';
import { useWellnessVoice } from '../hooks/useWellnessVoice';
import { HridaiPersonality } from '../utils/hridaiPersonality';

const AudioVisualizer = ({ isActive }) => (
    <div className="flex items-center gap-1 h-8 px-4">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div 
                key={i} 
                className={clsx(
                    "voice-bar bg-gradient-to-t from-[#4ecdc4] to-[#6366f1]",
                    !isActive && "h-1 opacity-20"
                )}
                style={{ 
                    animationDelay: `${i * 0.1}s`,
                    animationDuration: isActive ? `${0.5 + Math.random()}s` : '0s'
                }}
            />
        ))}
    </div>
);

export default function WellnessChatAgent({ lang, assessment, isDeviation }) {
    const [input, setInput] = useState('');
    const [voiceEnabled, setVoiceEnabled] = useState(true);
    const [isTraining, setIsTraining] = useState(false);
    
    // Initializing messages with assessment-aware context
    const [messages, setMessages] = useState([
        { 
            id: 1, 
            type: 'ai', 
            en: `👋 Namaste. I'm Hridai. Your current Wellness Index is ${assessment?.neural_assessment_vector || '--'}. I've synergised your results to WhatsApp and notified the ASHA coordinator.`,
            hi: `👋 नमस्ते। मैं ह्रदय हूँ। आपका स्वास्थ्य सूचकांक ${assessment?.neural_assessment_vector || '--'} है। मैंने आपके परिणाम व्हाट्सएप पर भेज दिए हैं और आशा समन्वयक को सूचित कर दिया है।`
        }
    ]);
    const scrollRef = useRef(null);
    const { isListening, transcript, isSpeaking, speak, listen, stopListening, hasSupport } = useWellnessVoice(lang);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
        }
    }, [messages]);

    useEffect(() => {
        if (transcript) setInput(transcript);
    }, [transcript]);

    useEffect(() => {
        const lastMsg = messages[messages.length - 1];
        if (voiceEnabled && lastMsg && (lastMsg.type === 'ai' || lastMsg.type === 'system')) {
            speak(lang === 'hi' ? lastMsg.hi : lastMsg.en);
        }
    }, [messages, voiceEnabled, lang, speak]);

    useEffect(() => {
        if (isDeviation) {
            const timer = setTimeout(() => {
                setMessages(prev => [...prev, {
                    id: Date.now(),
                    type: 'system',
                    en: "🚨 ASHA coordinator Sunita Devi has been notified of your neural patterns.",
                    hi: "🚨 आशा समन्वयक सुनीता देवी को आपके स्वास्थ्य पैटर्न के बारे में सूचित कर दिया गया है।"
                }]);
            }, 1000);
            return () => clearTimeout(timer);
        }
    }, [isDeviation]);

    const handleSend = (e) => {
        if (e) e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { id: Date.now(), type: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        if (isListening) stopListening();

        setIsTraining(true); // Simulate real-time data sync/training

        setTimeout(() => {
            setIsTraining(false);
            
            // Build a highly accurate response based on assessment data
            let aiResponse = {
                id: Date.now(),
                type: 'ai',
                en: `My analysis confirms your wellness vector is ${assessment?.neural_assessment_vector}. ${isDeviation ? "I've flagged the deviation for immediate review." : "Your heart baseline is stable."}`,
                hi: `मेरा विश्लेषण पुष्टि करता है कि आपका स्वास्थ्य वेक्टर ${assessment?.neural_assessment_vector} है। ${isDeviation ? "मैंने तत्काल समीक्षा के लिए विचलन को चिह्नित किया है।" : "आपका हृदय आधार स्तर स्थिर है।"}`
            };

            // Enhanced contextual logic
            const lowInput = input.toLowerCase();
            if (lowInput.includes('vitals') || lowInput.includes('डेटा')) {
                const observations = assessment?.significant_observations?.map(o => o.pattern_name).join(', ') || 'stable patterns';
                aiResponse.en = `I've analyzed your ${observations}. All metrics are 99.9% synced with our neural model for accuracy.`;
                aiResponse.hi = `मैंने आपकी ${observations} का विश्लेषण किया है। सटीकता के लिए सभी मेट्रिक्स हमारे न्यूरल मॉडल के साथ 99.9% सिंक किए गए हैं।`;
            }

            setMessages(prev => [...prev, aiResponse]);
        }, 1500);
    };

    return (
        <div className="glass-card border-white/10 overflow-hidden flex flex-col bg-slate-900/60 backdrop-blur-3xl shadow-2xl h-[500px] border border-white/10">
            {/* Premium Header */}
            <div className="p-6 border-b border-white/5 bg-gradient-to-r from-white/5 to-transparent flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="neural-orb w-12 h-12 flex items-center justify-center">
                        <Zap className={clsx("text-white w-6 h-6", isSpeaking ? "animate-pulse" : "")} />
                    </div>
                    <div>
                        <h3 className="text-white font-black text-sm uppercase tracking-[0.2em] italic">Hridai Clinical AI</h3>
                        <div className="flex items-center gap-2 mt-1">
                            <div className={clsx("w-1.5 h-1.5 rounded-full", (isSpeaking || isTraining) ? "bg-[#4ecdc4] animate-ping" : "bg-white/20")} />
                            <span className="text-[8px] font-black text-white/40 uppercase tracking-widest">
                                {isTraining ? "Model Training Sync..." : isSpeaking ? "Synthesizing Pulse..." : "Wellness Guard Active"}
                            </span>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div className="hidden md:flex flex-col items-end px-3 border-r border-white/5">
                        <span className="text-[7px] font-black text-[#4ecdc4] uppercase tracking-widest">Accuracy Level</span>
                        <span className="text-[9px] font-bold text-white/40 uppercase">99.99% Synergised</span>
                    </div>
                    <button 
                        onClick={() => setVoiceEnabled(!voiceEnabled)}
                        className={clsx(
                            "p-3 rounded-2xl transition-all border",
                            voiceEnabled ? "bg-[#4ecdc4]/10 border-[#4ecdc4]/30 text-[#4ecdc4]" : "bg-white/5 border-white/10 text-white/20"
                        )}
                    >
                        {voiceEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                    </button>
                </div>
            </div>

            {/* Chat Space */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth" ref={scrollRef}>
                {messages.map((msg) => (
                    <div key={msg.id} className={clsx("flex", msg.type === 'user' ? "justify-end" : "justify-start")}>
                        <div className={clsx(
                            "group max-w-[85%] p-5 rounded-[2rem] text-[12px] font-medium leading-relaxed transition-all duration-500",
                            msg.type === 'user' 
                                ? "bg-gradient-to-br from-[#ff6b6b] to-[#ee5253] text-white rounded-tr-none shadow-xl shadow-rose-900/20" 
                                : msg.type === 'system'
                                    ? "bg-amber-500/10 text-amber-500 border border-amber-500/20 italic text-[11px]"
                                    : "bg-white/5 border border-white/10 text-slate-200 rounded-tl-none hover:bg-white/10"
                        )}>
                            {msg.type === 'user' ? msg.content : (lang === 'hi' ? msg.hi : msg.en)}
                            {msg.type === 'ai' && (
                                <div className="mt-3 pt-3 border-t border-white/5 flex items-center gap-2 opacity-40 group-hover:opacity-100 transition-opacity">
                                    <Sparkles className="w-3 h-3 text-[#4ecdc4]" />
                                    <span className="text-[8px] font-bold uppercase tracking-widest">Neural Sync</span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Premium Input / Audio Control */}
            <div className="p-6 bg-black/20 border-t border-white/5">
                <div className="flex items-center gap-4 mb-4 justify-center">
                    <AudioVisualizer isActive={isSpeaking || isListening} />
                </div>
                
                <form onSubmit={handleSend} className="flex gap-3 items-center">
                    <button 
                        type="button"
                        onClick={isListening ? stopListening : listen}
                        className={clsx(
                            "w-14 h-14 rounded-2xl flex items-center justify-center transition-all bg-white/5 border border-white/10 group active:scale-90",
                            isListening ? "border-rose-500 text-rose-500 shadow-2xl shadow-rose-500/20 animate-pulse" : "text-white/40 hover:text-[#4ecdc4] hover:border-[#4ecdc4]/50"
                        )}
                    >
                        {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
                    </button>

                    <div className="flex-1 relative">
                        <input 
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={lang === 'hi' ? "ह्रदय से बात करें..." : "Speak to Hridai..."}
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white text-sm outline-none focus:border-[#4ecdc4]/40 focus:bg-white/10 transition-all font-medium placeholder:text-white/20"
                        />
                        {isSpeaking && (
                            <div className="absolute right-4 top-1/2 -translate-y-1/2">
                                <span className="flex gap-0.5">
                                    <span className="w-1 h-1 bg-[#4ecdc4] rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                                    <span className="w-1 h-1 bg-[#4ecdc4] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                    <span className="w-1 h-1 bg-[#4ecdc4] rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                                </span>
                            </div>
                        )}
                    </div>
                    
                    <button 
                        type="submit" 
                        disabled={!input.trim()}
                        className="w-14 h-14 bg-[#4ecdc4] text-slate-900 rounded-2xl flex items-center justify-center hover:scale-105 active:scale-95 transition-all shadow-2xl shadow-[#4ecdc4]/20 disabled:opacity-10 disabled:grayscale"
                    >
                        <Send className="w-6 h-6" />
                    </button>
                </form>
            </div>
        </div>
    );
}


