import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Roadmap } from '../../types';
import { StatusBadge, Badge } from '../common/Badge';
import { ProgressBar } from '../common/ProgressBar';
import { ChevronRight, ListTodo } from 'lucide-react';

interface RoadmapCardProps {
  roadmap: Roadmap;
}

export const RoadmapCard: React.FC<RoadmapCardProps> = ({ roadmap }) => {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/roadmaps/${roadmap.id}`)}
      className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 hover:border-blue-500/50 hover:bg-slate-900/95 transition-all duration-200 cursor-pointer group shadow-lg flex flex-col justify-between h-full"
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <StatusBadge status={roadmap.status} />
          {roadmap.effort && (
            <Badge variant="neutral" className="text-[10px] font-semibold bg-slate-950 border border-slate-800 text-slate-400">
              Effort: {roadmap.effort}
            </Badge>
          )}
        </div>

        <h3 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors line-clamp-2 leading-snug">
          {roadmap.title}
        </h3>

        {roadmap.description && (
          <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
            {roadmap.description}
          </p>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-3">
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-[11px] font-semibold text-slate-400">
            <span>Overall Progress</span>
            <span className="font-mono text-emerald-400">{roadmap.progress}%</span>
          </div>
          <ProgressBar progress={roadmap.progress} size="sm" />
        </div>

        <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
          <div className="flex items-center gap-1.5 font-medium">
            <ListTodo className="w-3.5 h-3.5 text-blue-400" />
            <span>{roadmap.tasks ? roadmap.tasks.length : 0} Tasks</span>
          </div>

          <div className="flex items-center gap-1 group-hover:translate-x-1 transition-transform text-blue-400 font-bold text-xs">
            <span>View Workflow</span>
            <ChevronRight className="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>
  );
};
