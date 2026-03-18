import React, { useState } from 'react';
import api from '../api';
import { Activity, ArrowRight, Loader2, User, Ruler, HeartPulse, Gauge, Zap } from 'lucide-react';
import clsx from 'clsx';

const API_ENDPOINT = "/brain/vitals/ingest";


export default function VitalsForm({ onComplete, isLowEnd }) {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        age: 30,
        sex: 'M',
        bmi: 24.0,
        hr: 75,
        sbp: 120,
        dbp: 80,
        symptoms: []
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        const payload = {
            age: parseInt(formData.age),
            sex: formData.sex,
            bmi: parseFloat(formData.bmi),
            current_vitals: {
                hr: parseInt(formData.hr),
                sbp: parseInt(formData.sbp),
                dbp: parseInt(formData.dbp)
            },
            symptoms: formData.symptoms,
            history_flags: {}
        };

        try {
            const response = await api.post(API_ENDPOINT, payload);
            onComplete(response.data);
            
            // Also store metric locally in the Gateway DB for history
            await api.post('/metrics/ingest', {
              metric_type: 'vital_pulse',
              value: payload.current_vitals.hr,
              source: 'patient_input',
              quality_score: 1.0,
              metadata: { sbp: payload.current_vitals.sbp, dbp: payload.current_vitals.dbp }
            });

        } catch (err) {
            alert("Neural Link Interrupted: " + (err.response?.data?.message || err.message));
        } finally {
            setLoading(false);
        }
    };


    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        if (type === 'checkbox') {
            const newSymptoms = checked 
                ? [...formData.symptoms, value]
                : formData.symptoms.filter(s => s !== value);
            setFormData({ ...formData, symptoms: newSymptoms });
        } else {
            setFormData({ ...formData, [name]: value });
        }
    };

    return (
        <div className={clsx(
            "glass-card p-6 border-white/10",
            !isLowEnd && "animate-in fade-in slide-in-from-bottom-4 duration-700"
        )}>
            <div className="mb-8">
                <h2 className="text-2xl font-black text-white uppercase tracking-tight italic">
                    Health <span className="text-[#ff6b6b]">Biometrics</span>
                </h2>
                <p className="text-white/40 text-[10px] font-bold uppercase tracking-widest mt-1">
                    Enter neural pulse and lifestyle metrics
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                        <label className="text-[10px] font-black text-white/40 uppercase tracking-widest flex items-center gap-1.5">
                            <User className="w-3 h-3" /> Age
                        </label>
                        <input name="age" type="number" value={formData.age} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-lg font-black text-white outline-none focus:border-[#ff6b6b]/50 focus:bg-white/10 transition-all" required />
                    </div>
                    <div className="space-y-1.5">
                        <label className="text-[10px] font-black text-white/40 uppercase tracking-widest flex items-center gap-1.5">
                            <Activity className="w-3 h-3" /> Sex
                        </label>
                        <select name="sex" value={formData.sex} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-lg font-black text-white outline-none focus:border-[#ff6b6b]/50 focus:bg-white/10 transition-all appearance-none cursor-pointer">
                            <option value="M" className="bg-[#1a1f3a]">Male</option>
                            <option value="F" className="bg-[#1a1f3a]">Female</option>
                            <option value="O" className="bg-[#1a1f3a]">Other</option>
                        </select>
                    </div>
                </div>

                <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-white/40 uppercase tracking-widest flex items-center gap-1.5">
                        <Ruler className="w-3 h-3" /> Body Mass Index (BMI)
                    </label>
                    <input name="bmi" type="number" step="0.1" value={formData.bmi} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-lg font-black text-[#4ecdc4] outline-none focus:border-[#4ecdc4]/50 focus:bg-white/10 transition-all" required />
                </div>

                <div className="pt-4 border-t border-white/5">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                            <HeartPulse className="w-4 h-4 text-[#ff6b6b]" />
                            <span className="text-xs font-black text-white/80 uppercase tracking-widest">Vital Signs (Wellness Vector)</span>
                        </div>
                        <div className="flex items-center gap-1.5 bg-[#4ecdc4]/10 border border-[#4ecdc4]/20 px-2 py-1 rounded-md">
                            <Zap className="w-3 h-3 text-[#4ecdc4]" />
                            <span className="text-[8px] font-black text-[#4ecdc4] uppercase tracking-tighter">rPPG Beta Active</span>
                        </div>
                    </div>

                    <div className="space-y-5">
                        <div className="space-y-2">
                             <div className="flex justify-between items-end">
                                <label className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em] block">Pulse Rate (BPM)</label>
                                <span className="text-[8px] font-black text-white/30 uppercase tracking-[0.1em] italic">Camera/Optical Ingest enabled</span>
                            </div>
                            <div className="relative">
                                <input name="hr" type="number" value={formData.hr} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-3xl font-black text-white outline-none focus:border-[#ff6b6b] focus:bg-white/10 transition-all tracking-tighter" required />
                                <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                                    <div className="w-2 h-2 bg-rose-500 rounded-full animate-ping" />
                                    <span className="text-[10px] font-black text-[#ff6b6b] uppercase">Live</span>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-white/40 uppercase tracking-widest flex items-center gap-1.5">
                                    <Gauge className="w-3 h-3" /> Systolic
                                </label>
                                <input name="sbp" type="number" value={formData.sbp} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-xl font-black text-white outline-none focus:border-white/30 transition-all" required />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-white/40 uppercase tracking-widest flex items-center gap-1.5">
                                    <Gauge className="w-3 h-3" /> Diastolic
                                </label>
                                <input name="dbp" type="number" value={formData.dbp} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-xl font-black text-white outline-none focus:border-white/30 transition-all" required />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-3 pt-4 border-t border-white/5">
                    <label className="text-[10px] font-black text-white/40 uppercase tracking-widest block">Symptoms (Extraordinary Check)</label>
                    <div className="flex flex-wrap gap-2">
                        {['chest_pain', 'shortness_of_breath', 'dizziness'].map(symptom => (
                            <label key={symptom} className="flex-1 min-w-[120px]">
                                <input 
                                    type="checkbox" 
                                    name="symptoms" 
                                    value={symptom} 
                                    onChange={handleChange}
                                    className="peer hidden"
                                />
                                <div className="bg-white/5 border border-white/10 rounded-xl p-2.5 text-center cursor-pointer transition-all peer-checked:bg-[#ff6b6b]/20 peer-checked:border-[#ff6b6b] peer-checked:text-[#ff6b6b]">
                                    <span className="text-[10px] font-black uppercase tracking-tight">{symptom.replace('_', ' ')}</span>
                                </div>
                            </label>
                        ))}
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full mt-6 bg-gradient-to-r from-[#ff6b6b] to-[#ee5a6f] hover:scale-[1.02] active:scale-[0.98] transition-all text-white font-black py-5 rounded-2xl shadow-[0_10px_30px_rgba(255,107,107,0.3)] flex items-center justify-center gap-3 disabled:opacity-70 group"
                >
                    {loading ? (
                        <Loader2 className="animate-spin w-6 h-6" />
                    ) : (
                        <>
                            <span className="uppercase tracking-[0.2em] text-sm">Initiate Neural Analysis</span>
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </>
                    )}
                </button>
            </form>
        </div>
    );
}
