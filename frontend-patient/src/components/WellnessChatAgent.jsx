import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Zap, ShieldCheck, Send, User } from 'lucide-react';
import clsx from 'clsx';

export default function WellnessChatAgent({ lang, isDeviation }) {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([
        { 
            id: 1, 
            type: 'ai', 
            en: "👋 Namaste. I'm Aarogya, your wellness companion. I've updated your care team with your latest metrics.",
            hi: "👋 नमस्ते। मैं आरोग्य हूँ, आपकी स्वास्थ्य सखी। मैंने आपकी नवीनतम रिपोर्ट के साथ आपकी टीम को अपडेट कर दिया है।"
        }
    ]);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (isDeviation) {
            setMessages(prev => [
                ...prev,
                {
                    id: Date.now(),
                    type: 'system',
                    en: "🚨 ASHA coordinator Sunita Devi has been notified and is reviewing your neural patterns.",
                    hi: "🚨 आशा समन्वयक सुनीता देवी को सूचित कर दिया गया है और वे आपके स्वास्थ्य पैटर्न की समीक्षा कर रही हैं।"
                },
                {
                    id: Date.now() + 1,
                    type: 'ai',
                    en: "Please rest in a comfortable position. Your family has received a WhatsApp update with your live location.",
                    hi: "कृपया आरामदेह स्थिति में लेट जाएं। आपके परिवार को आपके लाइव लोकेशन के साथ व्हाट्सएप अपडेट मिल गया है।"
                }
            ]);
        }
    }, [isDeviation]);

    const handleSend = (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { id: Date.now(), type: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');

        // Mock AI Response
        setTimeout(() => {
            setMessages(prev => [...prev, {
                id: Date.now(),
                type: 'ai',
                en: "I understand. I'm continuously monitoring your wellness vector. Help is on the way.",
                hi: "मैं समझ रही हूँ। मैं आपके स्वास्थ्य डेटा की लगातार निगरानी कर रही हूँ। मदद रास्ते में है।"
            }]);
        }, 1000);
    };

    return (
        <div className="glass-card border-white/10 overflow-hidden flex flex-col bg-[#0a0e27]/40 backdrop-blur-3xl shadow-2xl h-[450px]">
            <div className="p-5 border-b border-white/5 bg-white/5 flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#4ecdc4] to-[#44a08d] flex items-center justify-center text-xl shadow-lg shadow-[#4ecdc4]/20">
                    <Zap className="text-white w-6 h-6 animate-pulse" />
                </div>
                <div>
                    <h3 className="text-white font-black text-sm uppercase tracking-tighter italic">Aarogya AI Agent</h3>
                    <p className="text-[9px] font-bold text-[#4ecdc4] uppercase tracking-[0.2em] flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 bg-[#4ecdc4] rounded-full animate-ping" />
                        Live Wellness Support
                    </p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-hide" ref={scrollRef}>
                {messages.map((msg) => (
                    <div key={msg.id} className={clsx(
                        "flex",
                        msg.type === 'user' ? "justify-end" : "justify-start"
                    )}>
                        <div className={clsx(
                            "max-w-[85%] p-4 rounded-2xl text-[11px] font-medium leading-relaxed shadow-lg",
                            msg.type === 'user' ? "bg-[#ff6b6b] text-white rounded-tr-none" : 
                            msg.type === 'system' ? "bg-amber-500/10 text-amber-500 border border-amber-500/20 text-[10px] italic" :
                            "bg-white/5 border border-white/10 text-white/90 rounded-tl-none"
                        )}>
                            {msg.type === 'user' ? msg.content : (lang === 'hi' ? msg.hi : msg.en)}
                        </div>
                    </div>
                ))}
            </div>

            <form onSubmit={handleSend} className="p-4 bg-white/5 border-t border-white/5 flex gap-2">
                <input 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={lang === 'hi' ? "संदेश लिखें..." : "Type your message..."}
                    className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-xs outline-none focus:border-[#4ecdc4]/50 transition-all font-medium"
                />
                <button type="submit" className="bg-[#4ecdc4] text-white p-3 rounded-xl hover:scale-105 active:scale-95 transition-all shadow-lg shadow-[#4ecdc4]/20">
                    <Send className="w-5 h-5" />
                </button>
            </form>
        </div>
    );
}
