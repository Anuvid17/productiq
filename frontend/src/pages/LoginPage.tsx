import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { User } from '../types';
import { Sparkles, Mail, Lock, UserCheck, ArrowRight, ShieldCheck, Cpu, Eye, EyeOff } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState<User['role']>('Product Manager');
  const [loading, setLoading] = useState(false);
  const { login, loginWithGoogle, loginAsDemo } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setTimeout(() => {
      login(email, name || undefined, role);
      setLoading(false);
      navigate(from, { replace: true });
    }, 600);
  };

  const handleGoogleSubmit = () => {
    setLoading(true);
    setTimeout(() => {
      loginWithGoogle();
      setLoading(false);
      navigate(from, { replace: true });
    }, 500);
  };

  const handleQuickDemo = (preset: 'pm' | 'engineer') => {
    setLoading(true);
    setTimeout(() => {
      loginAsDemo(preset);
      setLoading(false);
      navigate(from, { replace: true });
    }, 400);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 relative overflow-hidden font-sans">
      {/* Dynamic Background Glow Elements */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Glassmorphism Container */}
      <div className="w-full max-w-md bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-2xl p-8 shadow-2xl z-10 space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-blue-600/20 border border-blue-500/30 text-blue-400 mb-1 shadow-inner">
            <Sparkles className="w-7 h-7 animate-pulse" />
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            ProductIQ
          </h1>
          <p className="text-xs text-slate-400 font-medium">
            AI-Driven Product Intelligence & Developer Resolution Platform
          </p>
        </div>

        {/* Mode Switcher Tabs (Sign In vs Create Account) */}
        <div className="grid grid-cols-2 p-1 bg-slate-950/80 rounded-xl border border-slate-800 text-xs font-bold">
          <button
            type="button"
            onClick={() => setMode('signin')}
            className={`py-2 rounded-lg transition-all ${
              mode === 'signin'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => setMode('signup')}
            className={`py-2 rounded-lg transition-all ${
              mode === 'signup'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Google Sign-In Button */}
        <div>
          <button
            type="button"
            onClick={handleGoogleSubmit}
            disabled={loading}
            className="w-full py-2.5 px-4 bg-white hover:bg-slate-100 text-slate-900 font-semibold text-xs rounded-xl transition-all shadow-md flex items-center justify-center gap-2.5 border border-slate-200 active:scale-[0.99]"
          >
            <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Continue with Google</span>
          </button>
        </div>

        {/* Quick Demo Login Presets */}
        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block text-center">
            ⚡ Quick Demo Presets
          </span>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickDemo('pm')}
              disabled={loading}
              className="px-3 py-2 bg-blue-900/40 hover:bg-blue-800/60 text-blue-200 text-xs font-semibold rounded-lg border border-blue-700/60 transition-all flex items-center justify-center gap-1.5 shadow-sm active:scale-[0.98]"
            >
              <UserCheck className="w-3.5 h-3.5 text-blue-400" />
              <span>Product Manager</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('engineer')}
              disabled={loading}
              className="px-3 py-2 bg-purple-900/40 hover:bg-purple-800/60 text-purple-200 text-xs font-semibold rounded-lg border border-purple-700/60 transition-all flex items-center justify-center gap-1.5 shadow-sm active:scale-[0.98]"
            >
              <Cpu className="w-3.5 h-3.5 text-purple-400" />
              <span>Lead Engineer</span>
            </button>
          </div>
        </div>

        <div className="relative flex items-center justify-center">
          <div className="w-full border-t border-slate-800" />
          <span className="bg-slate-900 px-3 text-[11px] text-slate-500 uppercase tracking-wider font-mono absolute">
            {mode === 'signin' ? 'Or Sign In With Email' : 'Or Create New Account'}
          </span>
        </div>

        {/* Login / Signup Form */}
        <form onSubmit={handleFormSubmit} className="space-y-4">
          {/* Full Name (Signup mode only) */}
          {mode === 'signup' && (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Vance"
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 text-xs rounded-xl px-4 py-2.5 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none placeholder:text-slate-600 transition-all"
              />
            </div>
          )}

          {/* Work Email */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
              Work Email
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alex.vance@company.com"
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 text-xs rounded-xl pl-9 pr-4 py-2.5 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none placeholder:text-slate-600 transition-all"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 text-xs rounded-xl pl-9 pr-10 py-2.5 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none placeholder:text-slate-600 transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Role Selection Pills */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
              Target Role
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(['Product Manager', 'Lead Engineer', 'QA Lead', 'Administrator'] as User['role'][]).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setRole(r)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all text-left ${
                    role === r
                      ? 'bg-blue-600 text-white border border-blue-500 shadow-sm font-bold'
                      : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-slate-200'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl transition-all shadow-lg shadow-blue-900/40 flex items-center justify-center gap-2 group active:scale-[0.99]"
          >
            <span>{loading ? 'Authenticating...' : mode === 'signin' ? 'Sign In to ProductIQ' : 'Create Free Account'}</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </form>

        {/* Footer Security Badge */}
        <div className="pt-1 text-center flex items-center justify-center gap-1.5 text-[11px] text-slate-400 font-medium">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Enterprise Grade Model Authentication</span>
        </div>
      </div>
    </div>
  );
};
