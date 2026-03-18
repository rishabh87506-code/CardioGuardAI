import React from 'react';
import { Building2 as Hospital, MapPin, Ambulance } from 'lucide-react';
import clsx from 'clsx';

export default function WellnessTriagePanel({ lang, currentLevel = 'emergency' }) {
    const strings = {
        en: {
            title: "Healthcare Triage Network",
            levels: {
                emergency: { label: "Emergency", icon: "🔴", desc: "Immediate tertiary care (AIIMS/Max)" },
                urgent: { label: "Urgent", icon: "🟡", desc: "District Hospital or CHC" },
                routine: { label: "Routine", icon: "🟢", desc: "Primary Health Center (PHC)" }
            },
            hospitals: [
                { name: "AIIMS Delhi", dist: "5.2 km", time: "12 min", status: "Notified" },
                { name: "Max Hospital", dist: "3.8 km", time: "9 min", status: "Notified" },
                { name: "Kalkaji PHC", dist: "0.8 km", time: "3 min", status: "Standby" }
            ],
            ambulance: "108 Ambulance En Route • ETA: 6 min"
        },
        hi: {
            title: "स्वास्थ्य देखभाल ट्राइएज नेटवर्क",
            levels: {
                emergency: { label: "आपातकालीन", icon: "🔴", desc: "तत्काल तृतीयक देखभाल (AIIMS/Max)" },
                urgent: { label: "जरूरी", icon: "🟡", desc: "जिला अस्पताल या CHC" },
                routine: { label: "नियमित", icon: "🟢", desc: "प्राथमिक स्वास्थ्य केंद्र (PHC)" }
            },
            hospitals: [
                { name: "AIIMS दिल्ली", dist: "5.2 किमी", time: "12 मिनट", status: "अधिसूचित" },
                { name: "मैक्स अस्पताल", dist: "3.8 किमी", time: "9 मिनट", status: "अधिसूचित" },
                { name: "कालकाजी PHC", dist: "0.8 किमी", time: "3 मिनट", status: "स्टैंडबाय" }
            ],
            ambulance: "108 एम्बुलेंस रास्ते में है • ईटीए: 6 मिनट"
        }
    };

    const s = strings[lang] || strings.en;

    return (
        <div className="glass-card p-6 border-white/10 mb-6 bg-white/5">
            <h3 className="text-white font-black text-xs uppercase tracking-[0.4em] mb-6 flex items-center gap-3 italic">
                <Hospital className="w-4 h-4 text-[#4ecdc4]" /> {s.title}
            </h3>

            {/* Triage Levels */}
            <div className="space-y-3 mb-8">
                {Object.entries(s.levels).map(([key, level]) => (
                    <div key={key} className={clsx(
                        "p-4 rounded-2xl border flex items-center gap-4 transition-all",
                        currentLevel === key 
                            ? "bg-white/10 border-white/20 shadow-xl" 
                            : "bg-white/5 border-transparent opacity-40 grayscale"
                    )}>
                        <div className="text-2xl">{level.icon}</div>
                        <div className="flex-1">
                            <p className="text-white font-black text-[10px] uppercase tracking-widest">{level.label}</p>
                            <p className="text-white/50 text-[10px] uppercase tracking-tight font-bold">{level.desc}</p>
                        </div>
                        {currentLevel === key && (
                            <div className="bg-[#ff6b6b] text-white text-[8px] font-black px-2 py-1 rounded-full uppercase tracking-widest animate-pulse">
                                Current
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Network Grid */}
            <div className="grid grid-cols-2 gap-3 pb-4">
                {s.hospitals.map((h, i) => (
                    <div key={i} className="bg-black/20 p-4 rounded-2xl border border-white/5 flex flex-col items-center text-center group hover:bg-black/30 transition-all">
                        <MapPin className="w-5 h-5 text-indigo-400 mb-2 group-hover:scale-125 transition-transform" />
                        <p className="text-[11px] font-black text-white italic">{h.name}</p>
                        <p className="text-[9px] text-white/30 font-bold uppercase mt-1 tracking-tighter">{h.dist} • {h.time}</p>
                        <div className={clsx(
                             "mt-3 px-3 py-1 rounded-full text-[8px] font-black uppercase tracking-widest border",
                             h.status === 'Notified' || h.status === 'अधिसूचित' 
                                ? "bg-[#4ecdc4]/10 text-[#4ecdc4] border-[#4ecdc4]/30"
                                : "bg-white/5 text-white/30 border-white/10"
                        )}>
                            {h.status}
                        </div>
                    </div>
                ))}
                <div className="bg-rose-500/10 p-4 rounded-2xl border border-rose-500/30 flex flex-col items-center text-center col-span-1 group hover:bg-rose-500/20 transition-all">
                    <Ambulance className="w-6 h-6 text-[#ff6b6b] mb-2 animate-[bounce_2s_infinite]" />
                    <p className="text-[9px] font-black text-[#ff6b6b] uppercase leading-tight italic">{s.ambulance}</p>
                </div>
            </div>
        </div>
    );
}
