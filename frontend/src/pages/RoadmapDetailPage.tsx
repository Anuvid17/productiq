import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import type { Roadmap } from '../types';
import { StatusBadge, Badge } from '../components/common/Badge';
import { ProgressBar } from '../components/common/ProgressBar';
import { TaskCard } from '../components/roadmap/TaskCard';
import { ArrowLeft, Map, Loader2, AlertTriangle } from 'lucide-react';

export const RoadmapDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const navigate = useNavigate();

  const loadRoadmap = async () => {
    if (!id) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      // First attempt direct roadmap fetch
      const data = await api.getRoadmapById(id);
      setRoadmap(data);
    } catch {
      // Fallback search across feedback detail
      try {
        const roadmaps = await api.getRoadmaps();
        const found = roadmaps.find((r) => r.id === id);
        if (found) {
          setRoadmap(found);
        } else {
          setErrorMsg('Roadmap not found.');
        }
      } catch (err: any) {
        setErrorMsg('Failed to load roadmap details.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoadmap();
  }, [id]);

  const handleUpdateTask = async (taskId: string, progress: number, status: string) => {
    await api.updateTask(taskId, { progress, status });
    await loadRoadmap();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-16 space-y-4">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        <span className="text-sm text-slate-400">Loading roadmap workflow...</span>
      </div>
    );
  }

  if (errorMsg || !roadmap) {
    return (
      <div className="p-8 bg-rose-950/40 border border-rose-800/60 rounded-xl text-center space-y-4 max-w-lg mx-auto">
        <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto" />
        <h3 className="text-lg font-bold text-white">Roadmap Not Found</h3>
        <p className="text-xs text-rose-300">{errorMsg}</p>
        <button
          onClick={() => navigate('/roadmaps')}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700"
        >
          Back to Roadmaps Grid
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/roadmaps')}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Roadmaps</span>
        </button>
        <StatusBadge status={roadmap.status} />
      </div>

      {/* Roadmap Overview Box */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider mb-2">
              <Map className="w-4 h-4" />
              <span>Roadmap Details</span>
            </div>
            <h1 className="text-xl font-bold text-white">{roadmap.title}</h1>
            {roadmap.description && (
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">{roadmap.description}</p>
            )}
          </div>
          {roadmap.effort && <Badge variant="neutral">Effort: {roadmap.effort}</Badge>}
        </div>

        <ProgressBar progress={roadmap.progress} size="md" className="pt-2" />
      </div>

      {/* Developer Tasks Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">
            Developer Tasks ({roadmap.tasks ? roadmap.tasks.length : 0})
          </h2>
          <span className="text-xs text-slate-400">
            Updating progress will automatically recalculate roadmap state
          </span>
        </div>

        {roadmap.tasks && roadmap.tasks.length > 0 ? (
          <div className="space-y-4">
            {roadmap.tasks.map((task, idx) => (
              <TaskCard
                key={task.id}
                task={task}
                index={idx}
                onUpdateTask={handleUpdateTask}
              />
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-500 bg-slate-800/40 rounded-xl border border-slate-700/50">
            No tasks registered for this roadmap.
          </div>
        )}
      </div>
    </div>
  );
};
