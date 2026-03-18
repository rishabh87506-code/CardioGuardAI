import React, { useState } from 'react';
import api from '../api';
import { LogIn, UserPlus, Loader2, ShieldCheck } from 'lucide-react';

export default function AuthScreen({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    
    try {
      const response = await api.post(endpoint, formData);
      const { token, user } = response.data;
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      onLoginSuccess(user);
    } catch (err) {
      setError(err.response?.data?.message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="glass-card p-8 border-white/10 animate-in fade-in zoom-in duration-500">
      <div className="flex justify-center mb-6">
        <div className="p-4 bg-[#4ecdc4]/20 rounded-full border border-[#4ecdc4]/30 shadow-[0_0_30px_rgba(78,205,196,0.3)]">
          <ShieldCheck className="w-10 h-10 text-[#4ecdc4]" />
        </div>
      </div>
      
      <h2 className="text-3xl font-black text-white text-center uppercase tracking-tighter italic mb-2">
        {isLogin ? (
          <>Welcome <span className="text-[#ff6b6b]">Back</span></>
        ) : (
          <>Join <span className="text-[#4ecdc4]">CardioGuard</span></>
        )}
      </h2>
      <p className="text-white/40 text-[10px] text-center font-black uppercase tracking-[0.3em] mb-8">
        Secure Wellness Authentication
      </p>

      {error && (
        <div className="bg-rose-500/20 border border-rose-500/50 p-3 rounded-xl mb-6 text-rose-400 text-xs font-bold text-center">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {!isLogin && (
          <div className="space-y-1.5">
            <label className="text-[10px] font-black text-white/40 uppercase tracking-widest px-1">Full Name</label>
            <input 
              name="full_name" 
              type="text" 
              value={formData.full_name} 
              onChange={handleChange} 
              className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none focus:border-[#4ecdc4]/50 transition-all font-bold" 
              required 
            />
          </div>
        )}
        
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-white/40 uppercase tracking-widest px-1">Email Address</label>
          <input 
            name="email" 
            type="email" 
            value={formData.email} 
            onChange={handleChange} 
            className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none focus:border-[#4ecdc4]/50 transition-all font-bold" 
            placeholder="name@email.com"
            required 
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-white/40 uppercase tracking-widest px-1">Password</label>
          <input 
            name="password" 
            type="password" 
            value={formData.password} 
            onChange={handleChange} 
            className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none focus:border-[#4ecdc4]/50 transition-all font-bold" 
            placeholder="••••••••"
            required 
          />
        </div>

        {!isLogin && (
          <div className="space-y-1.5">
            <label className="text-[10px] font-black text-white/40 uppercase tracking-widest px-1">Phone (Optional)</label>
            <input 
              name="phone" 
              type="text" 
              value={formData.phone} 
              onChange={handleChange} 
              className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none focus:border-[#4ecdc4]/50 transition-all font-bold" 
              placeholder="+91 XXXXX XXXXX"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-4 bg-white text-[#0a0e27] hover:bg-[#4ecdc4] hover:text-white transition-all font-black py-4 rounded-xl flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="animate-spin w-5 h-5" />
          ) : (
            <>
              {isLogin ? <LogIn className="w-5 h-5" /> : <UserPlus className="w-5 h-5" />}
              <span className="uppercase tracking-widest text-xs">{isLogin ? 'Authorize Access' : 'Create Wellness Profile'}</span>
            </>
          )}
        </button>
      </form>

      <div className="mt-8 text-center">
        <button 
          onClick={() => setIsLogin(!isLogin)}
          className="text-white/40 hover:text-[#4ecdc4] text-[10px] font-black uppercase tracking-widest transition-colors"
        >
          {isLogin ? "Don't have a profile? Register" : "Already have a profile? Login"}
        </button>
      </div>
    </div>
  );
}
