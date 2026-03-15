import React from 'react';
import { MessageSquare, MapPin, Activity, ShieldAlert } from 'lucide-react';

export default function WellnessWhatsAppPanel({ lang }) {
    const strings = {
        en: {
            title: "WhatsApp Live Tracking",
            subtitle: "Real-time updates to family & caregivers",
            items: [
                { label: "Family Group", value: "✓ Updated 30s ago" },
                { label: "Live Location", value: "Sharing Active" },
                { label: "Vital Updates", value: "Every 2 min" }
            ]
        },
        hi: {
            title: "व्हाट्सएप लाइव ट्रैकिंग",
            subtitle: "परिवार और देखभाल करने वालों को रीयल-टाइम अपडेट",
            items: [
                { label: "पारिवारिक समूह", value: "✓ 30 सेकंड पहले अपडेट किया गया" },
                { label: "लाइव स्थान", value: "शेयरिंग सक्रिय है" },
                { label: "वाइटल अपडेट", value: "हर 2 मिनट में" }
            ]
        }
    };

    const s = strings[lang] || strings.en;

    return (
        <div className="bg-[#25D366]/5 border-2 border-[#25D366]/30 rounded-3xl p-6 mb-6">
            <div className="flex items-center gap-4 mb-5 pb-4 border-b border-[#25D366]/20">
                <div className="w-12 h-12 bg-[#25D366] rounded-2xl flex items-center justify-center shadow-lg shadow-[#25D366]/30 group-hover:scale-110 transition-transform">
                    <MessageSquare className="text-white w-7 h-7" />
                </div>
                <div>
                    <h3 className="text-white font-black text-lg italic uppercase tracking-tight flex items-center gap-2">
                        {s.title}
                        <span className="bg-[#25D366]/20 text-[#25D366] text-[8px] font-black px-2 py-1 rounded-full uppercase tracking-widest animate-pulse">Active</span>
                    </h3>
                    <p className="text-white/40 text-[10px] font-bold uppercase tracking-widest mt-0.5">{s.subtitle}</p>
                </div>
            </div>

            <div className="space-y-2">
                {s.items.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center p-4 bg-white/5 rounded-2xl border border-white/5 group hover:bg-white/10 transition-all cursor-default">
                        <span className="text-[10px] font-black text-white/50 uppercase tracking-widest">{item.label}</span>
                        <span className="text-[10px] font-black text-[#25D366] uppercase tracking-widest">{item.value}</span>
                    </div>
                ))}
            </div>

            <div className="mt-4 p-4 bg-white/5 rounded-2xl border border-dashed border-[#25D366]/30">
                <p className="text-[9px] font-black text-[#25D366]/80 uppercase tracking-tighter mb-2 flex items-center gap-2">
                    <ShieldAlert className="w-3 h-3" /> Recent Activity:
                </p>
                <ul className="space-y-1.5 opacity-60">
                    <li className="text-[10px] text-white">→ Location: Kalkaji shared with Priority 1 contacts</li>
                    <li className="text-[10px] text-white">→ Abnormal HR trend shared with Care Circle</li>
                </ul>
            </div>
        </div>
    );
}
