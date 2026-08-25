import React from 'react';
import { type LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: string;
  trendType?: 'positive' | 'negative' | 'neutral';
  colorClass?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  description,
  trend,
  trendType = 'positive',
  colorClass = 'text-blue-400 bg-blue-500/10 border-blue-500/20',
}) => {
  return (
    <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-lg hover:border-slate-700/80 hover:-translate-y-0.5 transition-all duration-200 group relative overflow-hidden">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400 group-hover:text-slate-200 transition-colors">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl border ${colorClass} transition-transform group-hover:scale-105 duration-200 shrink-0`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline justify-between gap-2">
        <span className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight font-sans">
          {value}
        </span>
        {trend && (
          <span
            className={`text-[11px] font-bold px-2 py-0.5 rounded-md border shrink-0 ${
              trendType === 'positive'
                ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                : trendType === 'negative'
                ? 'text-rose-400 bg-rose-500/10 border-rose-500/20'
                : 'text-slate-400 bg-slate-800/80 border-slate-700/60'
            }`}
          >
            {trend}
          </span>
        )}
      </div>
      {description && (
        <p className="mt-2 text-xs text-slate-400 font-medium line-clamp-1 leading-relaxed">
          {description}
        </p>
      )}
    </div>
  );
};
