import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquarePlus,
  Map,
  Bell,
  Cpu,
  PlusCircle,
  User,
  Settings
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/feedback', label: 'Feedback', icon: MessageSquarePlus },
    { to: '/roadmaps', label: 'Roadmaps', icon: Map },
    { to: '/notifications', label: 'Notifications', icon: Bell },
    { to: '/profile', label: 'My Profile', icon: User },
  ];

  return (
    <aside className="w-64 bg-slate-950/95 backdrop-blur-xl border-r border-slate-800/80 flex flex-col h-screen sticky top-0 z-30 transition-all">
      {/* Brand Logo */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800/80">
        <div className="p-2 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-xl text-white shadow-lg shadow-blue-950/50">
          <Cpu className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <span className="text-lg font-extrabold tracking-tight text-white flex items-center gap-1">
            Product<span className="text-blue-500">IQ</span>
          </span>
          <span className="block text-[10px] text-slate-400 uppercase tracking-widest font-semibold">
            AI Product Intelligence
          </span>
        </div>
      </div>

      {/* Quick Action Submit Button */}
      <div className="p-4">
        <NavLink
          to="/feedback/new"
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white py-2.5 px-4 rounded-xl font-bold text-xs transition-all duration-200 shadow-lg shadow-blue-900/30 hover:shadow-blue-900/50 hover:scale-[1.02] active:scale-[0.98]"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Submit Feedback</span>
        </NavLink>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 px-3 py-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-950/50 translate-x-1'
                    : 'text-slate-400 hover:bg-slate-900/80 hover:text-slate-200 hover:translate-x-0.5'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer System Info */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="flex items-center gap-2.5 px-2 py-1.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-slate-400">
          <Settings className="w-4 h-4 text-blue-400 shrink-0" />
          <span className="text-[11px] font-medium truncate">Model: llama3.1 (Local)</span>
        </div>
      </div>
    </aside>
  );
};
