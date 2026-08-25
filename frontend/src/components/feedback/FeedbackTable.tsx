import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Feedback } from '../../types';
import { PriorityBadge, SeverityBadge, StatusBadge } from '../common/Badge';
import { MessageSquare, Calendar } from 'lucide-react';

interface FeedbackTableProps {
  items: Feedback[];
  loading?: boolean;
}

export const FeedbackTable: React.FC<FeedbackTableProps> = ({ items, loading }) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="w-full space-y-3 p-2">
        {[1, 2, 3, 4, 5].map((n) => (
          <div key={n} className="h-16 bg-slate-900/60 border border-slate-800/60 animate-pulse rounded-xl" />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 text-sm font-medium">
        No feedback records found.
      </div>
    );
  }

  return (
    <>
      {/* Desktop & Tablet Table Layout */}
      <div className="hidden sm:block overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-[11px] font-bold uppercase tracking-wider bg-slate-950/40">
              <th className="py-3.5 px-4">Feedback Summary</th>
              <th className="py-3.5 px-4">Type / Category</th>
              <th className="py-3.5 px-4">Severity</th>
              <th className="py-3.5 px-4">Priority</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-sm">
            {items.map((item) => (
              <tr
                key={item.id}
                onClick={() => navigate(`/feedback/${item.id}`)}
                className="hover:bg-slate-800/60 cursor-pointer transition-colors duration-150 group"
              >
                <td className="py-4 px-4 max-w-xs md:max-w-md">
                  <div className="flex items-start gap-3">
                    <MessageSquare className="w-4 h-4 text-blue-400 mt-0.5 group-hover:scale-110 transition-transform shrink-0" />
                    <div className="space-y-0.5">
                      <span
                        className="font-bold text-slate-100 group-hover:text-blue-400 transition-colors block line-clamp-1 text-xs sm:text-sm"
                        title={item.summary || item.original_text}
                      >
                        {item.summary || item.original_text}
                      </span>
                      <span
                        className="text-xs text-slate-400 line-clamp-1 leading-relaxed font-normal"
                        title={item.original_text}
                      >
                        {item.original_text}
                      </span>
                    </div>
                  </div>
                </td>
                <td className="py-4 px-4 text-xs">
                  <span className="font-bold text-slate-200 block">{item.feedback_type || 'Unclassified'}</span>
                  <span className="text-slate-400 font-medium">
                    {item.category || 'General'} {item.subcategory ? `› ${item.subcategory}` : ''}
                  </span>
                </td>
                <td className="py-4 px-4">
                  <SeverityBadge severity={item.severity} />
                </td>
                <td className="py-4 px-4">
                  <PriorityBadge priority={item.priority} />
                </td>
                <td className="py-4 px-4">
                  <StatusBadge status={item.status} />
                </td>
                <td className="py-4 px-4 text-xs text-slate-400 font-medium whitespace-nowrap">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    <span>
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card Grid Layout (< 640px) */}
      <div className="block sm:hidden space-y-3">
        {items.map((item) => (
          <div
            key={item.id}
            onClick={() => navigate(`/feedback/${item.id}`)}
            className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl space-y-3 cursor-pointer hover:border-slate-700 transition-all active:scale-[0.99]"
          >
            <div className="flex items-start justify-between gap-2">
              <span className="font-bold text-slate-100 text-xs line-clamp-2">
                {item.summary || item.original_text}
              </span>
              <StatusBadge status={item.status} />
            </div>

            <p className="text-xs text-slate-400 line-clamp-2">
              {item.original_text}
            </p>

            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-[11px]">
              <span className="text-slate-300 font-medium">
                {item.feedback_type || 'Unclassified'} • <span className="text-slate-400">{item.category || 'General'}</span>
              </span>
              <div className="flex items-center gap-1.5">
                <PriorityBadge priority={item.priority} />
                <SeverityBadge severity={item.severity} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
};
