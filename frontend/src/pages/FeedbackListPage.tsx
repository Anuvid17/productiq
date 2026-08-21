import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import type { Feedback } from '../types';
import { FeedbackTable } from '../components/feedback/FeedbackTable';
import { EmptyState } from '../components/common/EmptyState';
import { CustomDropdown } from '../components/common/CustomDropdown';
import { Search, ChevronLeft, ChevronRight, RefreshCw, Filter } from 'lucide-react';

export const FeedbackListPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [items, setItems] = useState<Feedback[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters state
  const page = Number(searchParams.get('page')) || 1;
  const pageSize = 20;
  const statusFilter = searchParams.get('status') || '';
  const priorityFilter = searchParams.get('priority') || '';
  const severityFilter = searchParams.get('severity') || '';
  const searchFilter = searchParams.get('search') || '';

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.getFeedback({
        page,
        page_size: pageSize,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        severity: severityFilter || undefined,
        search: searchFilter || undefined,
      });
      setItems(res.items);
      setTotal(res.total);
    } catch {
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [searchParams]);

  const updateParam = (key: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'Triaged', label: 'Triaged' },
    { value: 'Open', label: 'Open' },
    { value: 'In Review', label: 'In Review' },
    { value: 'Approved', label: 'Approved' },
    { value: 'Resolved', label: 'Resolved' },
  ];

  const priorityOptions = [
    { value: '', label: 'All Priorities' },
    { value: 'P0', label: 'P0 - Blocker' },
    { value: 'P1', label: 'P1 - High' },
    { value: 'P2', label: 'P2 - Medium' },
    { value: 'P3', label: 'P3 - Low' },
  ];

  const severityOptions = [
    { value: '', label: 'All Severities' },
    { value: 'Blocker', label: 'Blocker' },
    { value: 'Critical', label: 'Critical' },
    { value: 'Major', label: 'Major' },
    { value: 'Minor', label: 'Minor' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
            Feedback Intelligence Repository
          </h1>
          <p className="text-xs text-slate-400">
            Browse, search, and filter analyzed product feedback
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-all self-start sm:self-auto"
          title="Refresh Data"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Search & Custom Dropdowns Bar */}
      <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-lg space-y-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider mb-1">
          <Filter className="w-4 h-4" />
          <span>Interactive Filter Controls</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Search Input */}
          <div className="relative sm:col-span-2">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search feedback text..."
              value={searchFilter}
              onChange={(e) => updateParam('search', e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-xl pl-10 pr-4 py-2.5 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none placeholder:text-slate-500 transition-all"
            />
          </div>

          {/* Custom Status Dropdown */}
          <CustomDropdown
            value={statusFilter}
            options={statusOptions}
            onChange={(val) => updateParam('status', val)}
            placeholder="All Statuses"
          />

          {/* Custom Priority Dropdown */}
          <CustomDropdown
            value={priorityFilter}
            options={priorityOptions}
            onChange={(val) => updateParam('priority', val)}
            placeholder="All Priorities"
          />

          {/* Custom Severity Dropdown */}
          <CustomDropdown
            value={severityFilter}
            options={severityOptions}
            onChange={(val) => updateParam('severity', val)}
            placeholder="All Severities"
          />
        </div>
      </div>

      {/* Main Table View */}
      <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-xl animate-slide-up">
        {items.length > 0 ? (
          <>
            <FeedbackTable items={items} loading={loading} />

            {/* Pagination Controls */}
            <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <span className="font-mono">
                Page {page} of {totalPages} ({total} total entries)
              </span>

              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => updateParam('page', String(page - 1))}
                  className="px-3.5 py-1.5 bg-slate-950 hover:bg-slate-800 disabled:opacity-40 text-slate-300 rounded-xl border border-slate-800 transition-all flex items-center gap-1 font-semibold"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => updateParam('page', String(page + 1))}
                  className="px-3.5 py-1.5 bg-slate-950 hover:bg-slate-800 disabled:opacity-40 text-slate-300 rounded-xl border border-slate-800 transition-all flex items-center gap-1 font-semibold"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <EmptyState
            title="No Matching Feedback Found"
            description="Try adjusting search terms or clear active filters."
          />
        )}
      </div>
    </div>
  );
};
