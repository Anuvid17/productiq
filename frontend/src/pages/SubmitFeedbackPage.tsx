import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { CustomDropdown } from '../components/common/CustomDropdown';
import { Sparkles, AlertCircle, CheckCircle2, Loader2, ArrowLeft, Cpu } from 'lucide-react';

export const SubmitFeedbackPage: React.FC = () => {
  const [feedbackText, setFeedbackText] = useState('');
  const [platform, setPlatform] = useState('Web');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const navigate = useNavigate();

  const platformOptions = [
    { value: 'Web', label: 'Web Platform' },
    { value: 'iOS', label: 'iOS Mobile App' },
    { value: 'Android', label: 'Android Mobile App' },
    { value: 'Desktop', label: 'Desktop Application' },
    { value: 'API', label: 'REST API Service' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackText.trim()) return;

    setIsSubmitting(true);
    setErrorMsg(null);
    setStepIndex(0);

    const interval = setInterval(() => {
      setStepIndex((prev) => (prev < 3 ? prev + 1 : prev));
    }, 2000);

    try {
      const res = await api.createFeedback({
        original_text: feedbackText.trim(),
        platform,
      });

      clearInterval(interval);
      navigate(`/feedback/${res.id}`);
    } catch (err: any) {
      clearInterval(interval);
      setIsSubmitting(false);
      const msg = err.response?.data?.detail?.error?.message || err.message || 'Failed to analyze feedback';
      setErrorMsg(msg);
    }
  };

  const steps = [
    'Understanding raw feedback input',
    'Classifying category & severity via llama3.1',
    'Checking duplicate candidate records',
    'Generating developer roadmap & task workflow',
  ];

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      {/* Back button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors group"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
        <span>Back to Dashboard</span>
      </button>

      <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 md:p-8 shadow-2xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-2xl bg-blue-600/20 border border-blue-500/30 text-blue-400 shadow-inner">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-white tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
              Submit Feedback for Analysis
            </h1>
            <p className="text-xs text-slate-400">
              Enter customer feedback or bug reports to run ProductIQ's AI intelligence pipeline
            </p>
          </div>
        </div>

        {!isSubmitting ? (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                Feedback Text
              </label>
              <textarea
                rows={6}
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder="Describe the issue, bug, or feature request (e.g. 'The login page freezes after clicking Sign In on the web platform')."
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 text-sm rounded-xl p-4 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none placeholder:text-slate-600 transition-all"
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                  Source Platform
                </label>
                <CustomDropdown
                  value={platform}
                  options={platformOptions}
                  onChange={setPlatform}
                />
              </div>
            </div>

            {errorMsg && (
              <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="pt-2 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-5 py-2.5 bg-slate-950 hover:bg-slate-800 text-slate-300 text-xs font-semibold rounded-xl transition-all border border-slate-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!feedbackText.trim()}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-blue-900/40 flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98]"
              >
                <Sparkles className="w-4 h-4" />
                <span>Analyze Feedback</span>
              </button>
            </div>
          </form>
        ) : (
          /* Unified Processing Loader */
          <div className="py-8 text-center space-y-6 animate-fade-in">
            <div className="inline-flex p-4 rounded-full bg-blue-600/20 border border-blue-500/40 text-blue-400 mb-2 shadow-2xl animate-pulse-glow">
              <Cpu className="w-8 h-8 animate-spin" />
            </div>

            <div>
              <h3 className="text-lg font-bold text-white mb-1">Analyzing Feedback with llama3.1...</h3>
              <p className="text-xs text-slate-400">
                Running ProductIQ intelligence pipeline. Please wait...
              </p>
            </div>

            <div className="max-w-md mx-auto bg-slate-950/90 border border-slate-800 rounded-2xl p-5 text-left space-y-3.5 shadow-xl">
              {steps.map((label, i) => {
                const isDone = i < stepIndex;
                const isCurrent = i === stepIndex;
                return (
                  <div key={i} className="flex items-center gap-3 text-xs">
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-4 h-4 text-blue-400 animate-spin shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-slate-800 shrink-0" />
                    )}
                    <span className={isDone ? 'text-slate-200 font-medium' : isCurrent ? 'text-blue-400 font-bold' : 'text-slate-500'}>
                      {label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
