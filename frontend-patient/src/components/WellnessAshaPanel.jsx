import React from 'react';
import { User, Phone, MapPin, CheckCircle } from 'lucide-react';

export default function WellnessAshaPanel({ lang }) {
    const strings = {
        en: {
            title: "ASHA Wellness Coordinator",
            contact: "+91 98765 43210",
            status: "Available & Notified",
            area: "Kalkaji Health Center",
            exp: "8 years",
            resp: "2 min avg"
        },
        hi: {
            title: "आशा स्वास्थ्य समन्वयक",
            contact: "+91 98765 43210",
            status: "उपलब्ध और अधिसूचित",
            area: "कालकाजी स्वास्थ्य केंद्र",
            exp: "8 वर्ष",
            resp: "2 मिनट औसत"
        }
    };

    const s = strings[lang] || strings.en;

    return (
        <div className="bg-gradient-to-br from-[#4ecdc4]/15 to-[#44a08d]/15 border-2 border-[#4ecdc4]/40 rounded-3xl p-6 mb-6 animate-in zoom-in-95 duration-500">
            <div className="flex items-center gap-4 mb-6 pb-4 border-b border-white/10">
                <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#4ecdc4] to-[#44a08d] flex items-center justify-center text-3xl shadow-lg shadow-[#4ecdc4]/20">
                    <User className="text-white w-8 h-8" />
                </div>
                <div className="flex-1">
                    <h3 className="text-white font-black text-lg italic uppercase tracking-tight">{s.title}: Sunita Devi</h3>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1">
                        <p className="text-white/40 text-[10px] font-bold uppercase flex items-center gap-1.5 whitespace-nowrap">
                            <Phone className="w-2.5 h-2.5" /> {s.contact}
                        </p>
                        <p className="text-white/40 text-[10px] font-bold uppercase flex items-center gap-1.5 whitespace-nowrap">
                            <MapPin className="w-2.5 h-2.5" /> {s.area}
                        </p>
                    </div>
                    <p className="text-[#4ecdc4] text-[10px] font-black uppercase tracking-widest mt-2 flex items-center gap-1.5">
                        <CheckCircle className="w-3 h-3" /> {s.status}
                    </p>
                </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
                <div className="bg-black/20 rounded-2xl p-4 border border-white/5 text-center group hover:bg-black/30 transition-colors">
                    <p className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em] mb-1">Experience</p>
                    <p className="text-lg font-black text-white italic">{s.exp}</p>
                </div>
                <div className="bg-black/20 rounded-2xl p-4 border border-white/5 text-center group hover:bg-black/30 transition-colors">
                    <p className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em] mb-1">Response Time</p>
                    <p className="text-lg font-black text-[#4ecdc4] italic">{s.resp}</p>
                </div>
            </div>
        </div>
    );
}
