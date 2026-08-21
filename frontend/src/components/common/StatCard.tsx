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
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-xl p-5 shadow-sm hover:border-slate-600/80 transition-all">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-400">{title}</span>
        <div className={`p-2.5 rounded-lg border ${colorClass}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl font-bold text-white tracking-tight">{value}</span>
        {trend && (
          <span
            className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
              trendType === 'positive'
                ? 'text-emerald-400 bg-emerald-500/10'
                : trendType === 'negative'
                ? 'text-rose-400 bg-rose-500/10'
                : 'text-slate-400 bg-slate-700/50'
            }`}
          >
            {trend}
          </span>
        )}
      </div>
      {description && (
        <p className="mt-2 text-xs text-slate-400">{description}</p>
      )}
    </div>
  );
};
