import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import type { FeedbackDetail } from '../types';
import { PriorityBadge, SeverityBadge, StatusBadge, ActionBadge, Badge } from '../components/common/Badge';
import { ProgressBar } from '../components/common/ProgressBar';
import { TaskCard } from '../components/roadmap/TaskCard';
import {
  ArrowLeft,
  MessageSquare,
  Sparkles,
  CopyCheck,
  Map,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Calendar,
  ExternalLink
} from 'lucide-react';

export const FeedbackDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<FeedbackDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchDetail = async () => {
    if (!id) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const data = await api.getFeedbackById(id);
      setDetail(data);
    } catch (err: any) {
      const msg = err.response?.data?.detail?.error?.message || 'Feedback not found';
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  const handleUpdateTask = async (taskId: string, progress: number, status: string) => {
    await api.updateTask(taskId, { progress, status });
    await fetchDetail();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-16 space-y-4">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        <span className="text-sm text-slate-400">Loading feedback intelligence...</span>
      </div>
    );
  }

  if (errorMsg || !detail) {
    return (
      <div className="p-8 bg-rose-950/40 border border-rose-800/60 rounded-xl text-center space-y-4 max-w-lg mx-auto">
        <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto" />
        <h3 className="text-lg font-bold text-white">Feedback Not Found</h3>
        <p className="text-xs text-rose-300">{errorMsg}</p>
        <button
          onClick={() => navigate('/feedback')}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700"
        >
          Return to Feedback List
        </button>
      </div>
    );
  }

  const { duplicate, roadmap } = detail;

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/feedback')}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Feedback List</span>
        </button>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-mono">ID: {detail.id}</span>
          <StatusBadge status={detail.status} />
        </div>
      </div>

      {/* Resolution Banner Alert */}
      {detail.status === 'Resolved' && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-800/80 text-emerald-300 flex items-start gap-3 shadow-sm">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-emerald-200">Your reported issue has been resolved.</h4>
            <p className="text-xs text-emerald-300/90 mt-0.5">
              All developer roadmap tasks have been completed and verified. You can now check the fix.
            </p>
          </div>
        </div>
      )}

      {/* SECTION 1: ORIGINAL FEEDBACK & SUMMARY */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
          <MessageSquare className="w-4 h-4" />
          <span>Original Feedback Input</span>
        </div>

        <p className="text-lg font-semibold text-white leading-relaxed">
          "{detail.original_text}"
        </p>

        {detail.summary && (
          <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-xs text-slate-300">
            <span className="text-slate-400 font-medium mr-1">AI Summary:</span>
            {detail.summary}
          </div>
        )}

        <div className="flex items-center gap-4 text-xs text-slate-400 pt-2 border-t border-slate-700/60">
          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-slate-500" />
            <span>Submitted: {detail.created_at ? new Date(detail.created_at).toLocaleString() : 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* SECTION 2: AI ANALYSIS & TAXONOMY */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-sm space-y-6">
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>AI Classification & Taxonomy</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Feedback Type</span>
            <span className="text-sm font-bold text-white">{detail.feedback_type || 'General'}</span>
          </div>

          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Category / Subcategory</span>
            <span className="text-sm font-bold text-white block">{detail.category || 'N/A'}</span>
            <span className="text-xs text-slate-400">{detail.subcategory}</span>
          </div>

          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Severity</span>
            <SeverityBadge severity={detail.severity} />
          </div>

          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Priority</span>
            <PriorityBadge priority={detail.priority} />
          </div>

          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Bug Category</span>
            <span className="text-sm font-semibold text-slate-200">{detail.bug_category || 'N/A'}</span>
          </div>

          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Impact Area</span>
            <span className="text-sm font-semibold text-slate-200">{detail.impact_area || 'All Users'}</span>
          </div>

          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Platform</span>
            <Badge variant="brand">{detail.platform || 'Web'}</Badge>
          </div>

          <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Recommended Action</span>
            <ActionBadge action={detail.recommended_action} />
          </div>
        </div>
      </div>

      {/* SECTION 3: DUPLICATE ANALYSIS */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
          <CopyCheck className="w-4 h-4" />
          <span>Duplicate Detection Intelligence</span>
        </div>

        {duplicate && duplicate.is_duplicate ? (
          <div className="p-5 rounded-xl bg-amber-950/40 border border-amber-800/70 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-amber-300 font-bold text-sm">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>DUPLICATE DETECTED</span>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-amber-900/80 border border-amber-700 text-amber-200">
                Similarity Score: {(duplicate.similarity_score * 100).toFixed(1)}%
              </span>
            </div>

            <p className="text-xs text-amber-200/90 leading-relaxed">
              This feedback appears similar to an existing issue record in ProductIQ.
            </p>

            {duplicate.matched_text && (
              <div className="p-3 bg-slate-950/80 rounded-lg border border-amber-900/50 text-xs text-slate-300">
                <span className="text-slate-400 font-medium block mb-1">Matched Existing Text:</span>
                "{duplicate.matched_text}"
              </div>
            )}

            {duplicate.matched_feedback_id && (
              <div className="pt-2 flex items-center gap-3">
                <button
                  onClick={() => navigate(`/feedback/${duplicate.matched_feedback_id}`)}
                  className="px-3.5 py-1.5 bg-amber-900/60 hover:bg-amber-800/80 text-amber-200 text-xs font-semibold rounded-lg border border-amber-700/80 transition-colors flex items-center gap-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>View Existing Feedback</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl text-xs text-slate-300 flex items-center justify-between">
            <span>✓ No duplicate feedback detected (Similarity score: 0.0%)</span>
            <span className="text-slate-500 font-mono text-[11px]">Unique Entry</span>
          </div>
        )}
      </div>

      {/* SECTION 4: ROADMAP & DEVELOPER TASKS */}
      {roadmap ? (
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
              <Map className="w-4 h-4" />
              <span>Developer Roadmap Workflow</span>
            </div>
            <StatusBadge status={roadmap.status} />
          </div>

          <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-white">{roadmap.title}</h3>
                {roadmap.description && (
                  <p className="text-xs text-slate-400 mt-1">{roadmap.description}</p>
                )}
              </div>
              {roadmap.effort && <Badge variant="neutral">Effort: {roadmap.effort}</Badge>}
            </div>

            <ProgressBar progress={roadmap.progress} size="md" className="pt-2" />
          </div>

          {/* TASKS LIST */}
          <div className="space-y-4 pt-2">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <span>Roadmap Tasks ({roadmap.tasks ? roadmap.tasks.length : 0})</span>
            </h4>

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
              <p className="text-xs text-slate-500 italic">No tasks generated for this roadmap.</p>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 text-center text-xs text-slate-400">
          No roadmap generated for this item (Merged duplicate or unlinked).
        </div>
      )}
    </div>
  );
};
