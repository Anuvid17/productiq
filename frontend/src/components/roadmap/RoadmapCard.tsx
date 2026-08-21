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
      className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 hover:border-blue-500/50 hover:bg-slate-800 transition-all cursor-pointer group shadow-sm flex flex-col justify-between"
    >
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <StatusBadge status={roadmap.status} />
          {roadmap.effort && (
            <Badge variant="neutral">Effort: {roadmap.effort}</Badge>
          )}
        </div>

        <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors line-clamp-2 mb-2">
          {roadmap.title}
        </h3>

        {roadmap.description && (
          <p className="text-xs text-slate-400 line-clamp-2 mb-4">
            {roadmap.description}
          </p>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-slate-700/60">
        <ProgressBar progress={roadmap.progress} size="sm" className="mb-3" />

        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1.5">
            <ListTodo className="w-3.5 h-3.5 text-blue-400" />
            <span>{roadmap.tasks ? roadmap.tasks.length : 0} Tasks</span>
          </div>

          <div className="flex items-center gap-1 group-hover:translate-x-0.5 transition-transform text-blue-400 font-medium">
            <span>View Workflow</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </div>
        </div>
      </div>
    </div>
  );
};
