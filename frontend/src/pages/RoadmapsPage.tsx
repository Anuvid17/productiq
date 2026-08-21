import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { Roadmap } from '../types';
import { RoadmapCard } from '../components/roadmap/RoadmapCard';
import { EmptyState } from '../components/common/EmptyState';
import { RefreshCw, Loader2 } from 'lucide-react';

export const RoadmapsPage: React.FC = () => {
  const [roadmaps, setRoadmaps] = useState<Roadmap[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadRoadmaps = async () => {
    setLoading(true);
    try {
      const data = await api.getRoadmaps();
      setRoadmaps(data);
    } catch {
      setRoadmaps([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoadmaps();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
            Product Roadmaps
          </h1>
          <p className="text-xs text-slate-400">
            Developer roadmap execution and progress tracking
          </p>
        </div>
        <button
          onClick={loadRoadmaps}
          className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-all self-start sm:self-auto"
          title="Refresh Data"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-16">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      ) : roadmaps.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {roadmaps.map((rm, idx) => (
            <div key={rm.id} className="animate-slide-up opacity-0" style={{ animationDelay: `${idx * 80}ms` }}>
              <RoadmapCard roadmap={rm} />
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Product Roadmaps Available"
          description="Developer roadmaps are generated automatically when feedback is processed."
          actionLabel="Submit Feedback"
          onAction={() => window.location.href = '/feedback/new'}
        />
      )}
    </div>
  );
};
