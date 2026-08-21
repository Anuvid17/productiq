import React, { useState } from 'react';
import type { RoadmapTask } from '../../types';
import { StatusBadge } from '../common/Badge';
import { ProgressBar } from '../common/ProgressBar';
import { CustomDropdown } from '../common/CustomDropdown';
import { CheckCircle2, AlertCircle, Save } from 'lucide-react';

interface TaskCardProps {
  task: RoadmapTask;
  index: number;
  onUpdateTask: (taskId: string, progress: number, status: string) => Promise<void>;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, index, onUpdateTask }) => {
  const [progressInput, setProgressInput] = useState<number>(task.progress);
  const [statusInput, setStatusInput] = useState<string>(task.status);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const statusOptions = [
    { value: 'Open', label: 'Open' },
    { value: 'In Review', label: 'In Review' },
    { value: 'Approved', label: 'Approved' },
    { value: 'In Progress', label: 'In Progress' },
    { value: 'Testing', label: 'Testing' },
    { value: 'Resolved', label: 'Resolved' },
    { value: 'Closed', label: 'Closed' },
  ];

  const handleUpdateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdating(true);
    setErrorMsg(null);
    try {
      await onUpdateTask(task.id, Number(progressInput), statusInput);
    } catch (err: any) {
      const msg = err.response?.data?.detail?.error?.message || err.message || 'Failed to update task';
      setErrorMsg(msg);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-lg transition-all duration-200 hover:border-slate-700 animate-slide-up">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-3">
          <span className="w-7 h-7 rounded-xl bg-blue-600/20 border border-blue-500/30 text-blue-400 font-bold text-xs flex items-center justify-center shadow-inner">
            {String(index + 1).padStart(2, '0')}
          </span>
          <h4 className="text-base font-bold text-white tracking-tight">{task.title}</h4>
        </div>
        <StatusBadge status={task.status} />
      </div>

      {task.description && (
        <p className="text-xs text-slate-300 mb-4 pl-10 leading-relaxed">
          {task.description}
        </p>
      )}

      {/* Acceptance Criteria */}
      {task.acceptance_criteria && task.acceptance_criteria.length > 0 && (
        <div className="pl-10 mb-4">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-2">
            Acceptance Criteria
          </span>
          <ul className="space-y-1.5">
            {task.acceptance_criteria.map((item, idx) => (
              <li key={idx} className="flex items-center gap-2 text-xs text-slate-300 bg-slate-950/60 p-2 rounded-xl border border-slate-800/80">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="pl-10 mb-4">
        <ProgressBar progress={task.progress} size="sm" />
      </div>

      {/* Interactive Task Update Form */}
      <form onSubmit={handleUpdateSubmit} className="pl-10 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="w-44">
            <CustomDropdown
              value={statusInput}
              options={statusOptions}
              onChange={setStatusInput}
            />
          </div>

          <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
            <label className="text-xs text-slate-400 font-semibold">Progress:</label>
            <input
              type="number"
              min="0"
              max="100"
              value={progressInput}
              onChange={(e) => setProgressInput(Number(e.target.value))}
              className="w-14 bg-slate-900 border border-slate-800 text-xs text-slate-100 rounded-lg px-2 py-1 text-center font-mono focus:border-blue-500 focus:outline-none"
            />
            <span className="text-xs text-slate-400 font-mono">%</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={isUpdating}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition-all shadow-md shadow-blue-950 flex items-center gap-1.5"
        >
          <Save className="w-3.5 h-3.5" />
          <span>{isUpdating ? 'Saving...' : 'Update Task'}</span>
        </button>
      </form>

      {errorMsg && (
        <div className="mt-2 ml-10 text-xs text-rose-400 flex items-center gap-1.5">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{errorMsg}</span>
        </div>
      )}
    </div>
  );
};
