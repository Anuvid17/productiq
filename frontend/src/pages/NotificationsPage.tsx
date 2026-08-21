import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import type { Notification } from '../types';
import { EmptyState } from '../components/common/EmptyState';
import { Bell, CheckCircle2, Check, RefreshCw, Calendar, Loader2 } from 'lucide-react';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false);
  const navigate = useNavigate();

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const data = await api.getNotifications(unreadOnly ? true : undefined);
      setNotifications(data);
    } catch {
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, [unreadOnly]);

  const handleMarkRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      );
    } catch {
      // ignore
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">System Notifications</h1>
          <p className="text-sm text-slate-400">
            Resolution alerts and internal system notifications
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-slate-300 font-medium cursor-pointer">
            <input
              type="checkbox"
              checked={unreadOnly}
              onChange={(e) => setUnreadOnly(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-blue-600 focus:ring-blue-500"
            />
            <span>Unread Only</span>
          </label>
          <button
            onClick={loadNotifications}
            className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-16">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      ) : notifications.length > 0 ? (
        <div className="space-y-3">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              onClick={() => navigate(`/feedback/${notif.feedback_id}`)}
              className={`p-4 rounded-xl border transition-all cursor-pointer flex items-start justify-between gap-4 ${
                notif.read
                  ? 'bg-slate-800/40 border-slate-800 text-slate-400'
                  : 'bg-slate-800 border-slate-700 text-slate-200 shadow-sm'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg mt-0.5 ${
                  notif.notification_type === 'RESOLUTION'
                    ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                    : 'bg-blue-500/10 border border-blue-500/20 text-blue-400'
                }`}>
                  {notif.notification_type === 'RESOLUTION' ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : (
                    <Bell className="w-4 h-4" />
                  )}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white mb-1">
                    {notif.notification_type === 'RESOLUTION' ? 'Issue Resolved' : 'System Alert'}
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed mb-2">{notif.message}</p>
                  <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                    <Calendar className="w-3 h-3" />
                    <span>{notif.created_at ? new Date(notif.created_at).toLocaleString() : 'Recent'}</span>
                  </div>
                </div>
              </div>

              {!notif.read && (
                <button
                  onClick={(e) => handleMarkRead(notif.id, e)}
                  className="px-2.5 py-1 text-xs font-semibold rounded bg-slate-900 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors flex items-center gap-1 shrink-0"
                >
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span>Mark Read</span>
                </button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Notifications Found"
          description={unreadOnly ? 'No unread notifications at this time.' : 'Resolution notifications will appear here when developer workflows complete.'}
        />
      )}
    </div>
  );
};
