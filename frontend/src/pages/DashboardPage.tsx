import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { api } from '../services/api';
import type { Feedback, Roadmap, DashboardSummary } from '../types';
import { StatCard } from '../components/common/StatCard';
import { FeedbackTable } from '../components/feedback/FeedbackTable';
import { RoadmapCard } from '../components/roadmap/RoadmapCard';
import { EmptyState } from '../components/common/EmptyState';
import {
  MessageSquare,
  AlertOctagon,
  CheckCircle,
  PlusCircle,
  ArrowRight,
  RefreshCw,
  PieChart,
  BarChart3,
  TrendingUp
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [feedbackItems, setFeedbackItems] = useState<Feedback[]>([]);
  const [roadmaps, setRoadmaps] = useState<Roadmap[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const sumData = await api.getDashboardSummary();
      setSummary(sumData);

      const res = await api.getFeedback({ page: 1, page_size: 5 });
      setFeedbackItems(res.items);

      const rms = await api.getRoadmaps({ limit: 3 });
      setRoadmaps(rms);
    } catch {
      setSummary(null);
      setFeedbackItems([]);
      setRoadmaps([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in pb-8">
      {/* Page Title & Top Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight font-sans">
            ProductIQ Intelligence Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 font-normal mt-0.5">
            Real-time AI product feedback analytics, duplicate detection, and developer workflows
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadDashboardData}
            disabled={loading}
            className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800/90 hover:border-slate-700 transition-all duration-200 active:scale-95 disabled:opacity-50"
            title="Refresh Dashboard Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
          <NavLink
            to="/feedback/new"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl font-bold text-xs transition-all duration-200 shadow-lg shadow-blue-900/30 hover:scale-[1.02] active:scale-[0.98]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Submit Feedback</span>
          </NavLink>
        </div>
      </div>

      {/* Summary Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="animate-slide-up opacity-0">
          <StatCard
            title="Total Feedback"
            value={summary ? summary.total_feedback : 0}
            icon={MessageSquare}
            description="Processed customer feedback entries"
            colorClass="text-blue-400 bg-blue-500/10 border-blue-500/20"
          />
        </div>
        <div className="animate-slide-up opacity-0 delay-100">
          <StatCard
            title="Open Issues"
            value={summary ? summary.open_feedback : 0}
            icon={AlertOctagon}
            description="Triaged & Open feedback requiring fix"
            colorClass="text-amber-400 bg-amber-500/10 border-amber-500/20"
          />
        </div>
        <div className="animate-slide-up opacity-0 delay-200">
          <StatCard
            title="Critical / P0"
            value={summary ? summary.critical_blocker_issues : 0}
            icon={AlertOctagon}
            description="Blocker & P0 high priority issues"
            colorClass="text-rose-400 bg-rose-500/10 border-rose-500/20"
          />
        </div>
        <div className="animate-slide-up opacity-0 delay-300">
          <StatCard
            title="Resolved Rate"
            value={summary ? `${summary.resolution_rate}%` : '0%'}
            icon={CheckCircle}
            description={`${summary ? summary.resolved_feedback : 0} feedback items fully resolved`}
            colorClass="text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
          />
        </div>
      </div>

      {/* Analytics Panels: Type, Priority, and Roadmap Analytics */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-slide-up opacity-0 delay-300">
          {/* Breakdown by Feedback Type */}
          <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-blue-400 uppercase tracking-wider">
                <PieChart className="w-4 h-4" />
                <span>Feedback by Type</span>
              </div>
              <span className="text-[11px] font-mono font-semibold text-slate-400 bg-slate-950 px-2 py-0.5 rounded-md border border-slate-800">
                {summary.total_feedback} Total
              </span>
            </div>
            <div className="space-y-3 pt-1 flex-1 flex flex-col justify-center">
              {Object.entries(summary.feedback_by_type).map(([k, v]) => {
                const pct = summary.total_feedback > 0 ? Math.round((v / summary.total_feedback) * 100) : 0;
                return (
                  <div key={k} className="text-xs space-y-1.5">
                    <div className="flex justify-between font-semibold text-slate-200">
                      <span>{k}</span>
                      <span className="font-mono text-slate-400">{v} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-800/80">
                      <div
                        className="bg-gradient-to-r from-blue-600 via-indigo-500 to-cyan-400 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
              {Object.keys(summary.feedback_by_type).length === 0 && (
                <span className="text-xs text-slate-500 italic block text-center py-4">No feedback types recorded.</span>
              )}
            </div>
          </div>

          {/* Breakdown by Priority */}
          <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider">
                <BarChart3 className="w-4 h-4" />
                <span>Feedback by Priority</span>
              </div>
              <span className="text-[11px] font-mono font-semibold text-slate-400 bg-slate-950 px-2 py-0.5 rounded-md border border-slate-800">
                Distribution
              </span>
            </div>
            <div className="space-y-3 pt-1 flex-1 flex flex-col justify-center">
              {Object.entries(summary.feedback_by_priority).map(([k, v]) => {
                const pct = summary.total_feedback > 0 ? Math.round((v / summary.total_feedback) * 100) : 0;
                const barColor =
                  k === 'P0'
                    ? 'bg-gradient-to-r from-rose-600 to-red-500'
                    : k === 'P1'
                    ? 'bg-gradient-to-r from-amber-500 to-orange-400'
                    : 'bg-gradient-to-r from-blue-500 to-cyan-400';
                return (
                  <div key={k} className="text-xs space-y-1.5">
                    <div className="flex justify-between font-semibold text-slate-200">
                      <span>{k} Priority</span>
                      <span className="font-mono text-slate-400">{v} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-800/80">
                      <div className={`${barColor} h-2.5 rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
              {Object.keys(summary.feedback_by_priority).length === 0 && (
                <span className="text-xs text-slate-500 italic block text-center py-4">No priority entries recorded.</span>
              )}
            </div>
          </div>

          {/* Roadmap Analytics Summary */}
          <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-wider">
                <TrendingUp className="w-4 h-4" />
                <span>Roadmap Analytics</span>
              </div>
              <span className="text-[11px] font-mono font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                Active
              </span>
            </div>
            <div className="space-y-3 pt-1 flex-1 flex flex-col justify-center text-xs">
              <div className="flex justify-between items-center p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
                <span className="text-slate-400 font-medium">Active Roadmaps</span>
                <span className="font-extrabold text-white text-base">{summary.active_roadmaps}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
                <span className="text-slate-400 font-medium">Average Progress</span>
                <span className="font-bold text-emerald-400 text-sm font-mono">{summary.average_roadmap_progress}%</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
                <span className="text-slate-400 font-medium">Resolution Rate</span>
                <span className="font-bold text-blue-400 text-sm font-mono">{summary.resolution_rate}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Recent Feedback & Active Roadmaps */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Feedback (2 cols) */}
        <div className="lg:col-span-2 bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-base font-extrabold text-white tracking-tight">Recent Feedback</h2>
              <p className="text-xs text-slate-400 font-normal">Latest analyzed feedback entries</p>
            </div>
            <NavLink
              to="/feedback"
              className="text-xs font-bold text-blue-400 hover:text-blue-300 flex items-center gap-1 group transition-colors"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </NavLink>
          </div>

          {feedbackItems.length > 0 ? (
            <FeedbackTable items={feedbackItems} loading={loading} />
          ) : (
            <EmptyState
              title="No Feedback Submitted Yet"
              description="Submit customer feedback to automatically trigger AI classification and roadmap generation."
              actionLabel="Submit First Feedback"
              onAction={() => window.location.href = '/feedback/new'}
            />
          )}
        </div>

        {/* Active Roadmaps (1 col) */}
        <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between mb-1">
            <div>
              <h2 className="text-base font-extrabold text-white tracking-tight">Active Roadmaps</h2>
              <p className="text-xs text-slate-400 font-normal">Developer progress tracking</p>
            </div>
            <NavLink
              to="/roadmaps"
              className="text-xs font-bold text-blue-400 hover:text-blue-300 flex items-center gap-1 group transition-colors"
            >
              <span>All Roadmaps</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </NavLink>
          </div>

          {roadmaps.length > 0 ? (
            <div className="space-y-4">
              {roadmaps.map((rm) => (
                <RoadmapCard key={rm.id} roadmap={rm} />
              ))}
            </div>
          ) : (
            <EmptyState
              title="No Active Roadmaps"
              description="Roadmaps are automatically created when new feedback is triaged."
            />
          )}
        </div>
      </div>
    </div>
  );
};
