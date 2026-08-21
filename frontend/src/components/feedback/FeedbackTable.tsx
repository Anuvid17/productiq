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
      <div className="w-full space-y-3 p-4">
        {[1, 2, 3, 4, 5].map((n) => (
          <div key={n} className="h-14 bg-slate-800/60 animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 text-sm">
        No feedback records found.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase tracking-wider bg-slate-950/40">
            <th className="py-3 px-4">Feedback Summary</th>
            <th className="py-3 px-4">Type / Category</th>
            <th className="py-3 px-4">Severity</th>
            <th className="py-3 px-4">Priority</th>
            <th className="py-3 px-4">Status</th>
            <th className="py-3 px-4">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 text-sm">
          {items.map((item) => (
            <tr
              key={item.id}
              onClick={() => navigate(`/feedback/${item.id}`)}
              className="hover:bg-slate-800/50 cursor-pointer transition-colors group"
            >
              <td className="py-3.5 px-4 max-w-md">
                <div className="flex items-start gap-2.5">
                  <MessageSquare className="w-4 h-4 text-slate-500 mt-0.5 group-hover:text-blue-400 transition-colors shrink-0" />
                  <div>
                    <span className="font-medium text-slate-200 group-hover:text-blue-400 transition-colors block line-clamp-1">
                      {item.summary || item.original_text}
                    </span>
                    <span className="text-xs text-slate-500 line-clamp-1">
                      {item.original_text}
                    </span>
                  </div>
                </div>
              </td>
              <td className="py-3.5 px-4 text-xs">
                <span className="font-semibold text-slate-300 block">{item.feedback_type || 'Unclassified'}</span>
                <span className="text-slate-500">{item.category || 'General'} {item.subcategory ? `› ${item.subcategory}` : ''}</span>
              </td>
              <td className="py-3.5 px-4">
                <SeverityBadge severity={item.severity} />
              </td>
              <td className="py-3.5 px-4">
                <PriorityBadge priority={item.priority} />
              </td>
              <td className="py-3.5 px-4">
                <StatusBadge status={item.status} />
              </td>
              <td className="py-3.5 px-4 text-xs text-slate-500 whitespace-nowrap">
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5" />
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
  );
};
