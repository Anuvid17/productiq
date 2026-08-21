import React, { useEffect, useState, useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Search, Bell, Activity, User as UserIcon, LogOut, ChevronDown, Sparkles, Moon, Sun, Zap } from 'lucide-react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { useTheme, type Theme } from '../../context/ThemeContext';
import type { HealthResponse } from '../../types';

export const Header: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isThemeMenuOpen, setIsThemeMenuOpen] = useState(false);

  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();

  const profileMenuRef = useRef<HTMLDivElement>(null);
  const themeMenuRef = useRef<HTMLDivElement>(null);

  const checkNotificationsAndHealth = () => {
    api.getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));

    api.getNotifications(false) // unread only
      .then((notifs) => setUnreadCount(notifs.length))
      .catch(() => setUnreadCount(0));
  };

  useEffect(() => {
    checkNotificationsAndHealth();
    const interval = setInterval(checkNotificationsAndHealth, 12000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setIsProfileMenuOpen(false);
      }
      if (themeMenuRef.current && !themeMenuRef.current.contains(event.target as Node)) {
        setIsThemeMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/feedback?search=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  const handleLogout = () => {
    setIsProfileMenuOpen(false);
    logout();
    navigate('/login');
  };

  const themeIcons: Record<Theme, React.ReactNode> = {
    dark: <Moon className="w-4 h-4 text-blue-400" />,
    cyber: <Zap className="w-4 h-4 text-cyan-400 animate-pulse" />,
    light: <Sun className="w-4 h-4 text-amber-400" />,
  };

  return (
    <header className="h-16 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-40 transition-all">
      {/* Global Search with Animated Focus Ring */}
      <form onSubmit={handleSearchSubmit} className="relative w-72">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          placeholder="Search feedback, bugs, roadmaps..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-slate-900/90 border border-slate-800 text-slate-200 text-xs rounded-xl pl-9 pr-4 py-2 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 placeholder:text-slate-500"
        />
      </form>

      {/* Right Toolbar */}
      <div className="flex items-center gap-3">
        {/* Backend Health Status Pill */}
        {health ? (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-xs shadow-inner">
            <span
              className={`w-2 h-2 rounded-full ${
                health.ollama.available ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
              }`}
            />
            <span className="text-slate-300 font-medium text-[11px]">
              API: {health.status}
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950/50 border border-rose-800/50 text-xs text-rose-400">
            <Activity className="w-3.5 h-3.5" />
            <span className="text-[11px]">Backend Offline</span>
          </div>
        )}

        {/* Theme Switcher Dropdown */}
        <div className="relative" ref={themeMenuRef}>
          <button
            type="button"
            onClick={() => setIsThemeMenuOpen(!isThemeMenuOpen)}
            className="p-2 rounded-xl text-slate-400 hover:bg-slate-900 hover:text-slate-200 transition-colors flex items-center gap-1"
            title="Switch Visual Style Theme"
          >
            {themeIcons[theme]}
          </button>

          {isThemeMenuOpen && (
            <div className="absolute right-0 top-full mt-2 w-48 bg-slate-900/95 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl overflow-hidden animate-dropdown-enter z-50 p-1.5 space-y-1">
              <span className="block px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Visual Theme
              </span>
              <button
                type="button"
                onClick={() => {
                  setTheme('dark');
                  setIsThemeMenuOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors ${
                  theme === 'dark'
                    ? 'bg-blue-600/20 text-blue-300 font-bold border border-blue-500/30'
                    : 'text-slate-300 hover:bg-slate-800/80'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Moon className="w-4 h-4 text-blue-400" />
                  <span>Midnight Dark</span>
                </div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setTheme('cyber');
                  setIsThemeMenuOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors ${
                  theme === 'cyber'
                    ? 'bg-cyan-600/20 text-cyan-300 font-bold border border-cyan-500/30'
                    : 'text-slate-300 hover:bg-slate-800/80'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-cyan-400" />
                  <span>Cyberpunk Neon</span>
                </div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setTheme('light');
                  setIsThemeMenuOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors ${
                  theme === 'light'
                    ? 'bg-amber-600/20 text-amber-300 font-bold border border-amber-500/30'
                    : 'text-slate-300 hover:bg-slate-800/80'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Sun className="w-4 h-4 text-amber-400" />
                  <span>Enterprise Light</span>
                </div>
              </button>
            </div>
          )}
        </div>

        {/* Notifications Icon Bell */}
        <NavLink
          to="/notifications"
          className="relative p-2 rounded-xl text-slate-400 hover:bg-slate-900 hover:text-slate-200 transition-colors"
          title="Notifications Center"
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-blue-600 text-white font-bold text-[10px] rounded-full flex items-center justify-center border-2 border-slate-950 animate-pulse">
              {unreadCount}
            </span>
          )}
        </NavLink>

        {/* Interactive Profile Dropdown */}
        {user ? (
          <div className="relative pl-3 border-l border-slate-800" ref={profileMenuRef}>
            <button
              type="button"
              onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
              className="flex items-center gap-2.5 p-1 rounded-xl hover:bg-slate-900/80 transition-colors focus:outline-none"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 border border-blue-400/50 flex items-center justify-center text-white font-bold text-xs shadow-md">
                {user.avatar || 'U'}
              </div>
              <div className="hidden md:block text-left text-xs">
                <span className="block font-semibold text-slate-200">{user.name}</span>
                <span className="block text-slate-400 text-[10px]">{user.role}</span>
              </div>
              <ChevronDown
                className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
                  isProfileMenuOpen ? 'rotate-180 text-blue-400' : ''
                }`}
              />
            </button>

            {/* Profile Dropdown Panel */}
            {isProfileMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-64 bg-slate-900/95 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl overflow-hidden animate-dropdown-enter z-50">
                {/* Header User Card */}
                <div className="p-4 bg-slate-950/60 border-b border-slate-800 space-y-1">
                  <span className="block text-xs font-bold text-white truncate">{user.name}</span>
                  <span className="block text-[11px] text-slate-400 font-mono truncate">{user.email}</span>
                  <div className="pt-1">
                    <span className="inline-block px-2 py-0.5 rounded-md bg-blue-600/20 text-blue-300 font-semibold text-[10px] border border-blue-500/30">
                      {user.role}
                    </span>
                  </div>
                </div>

                {/* Dropdown Options */}
                <div className="p-2 space-y-1">
                  <button
                    type="button"
                    onClick={() => {
                      setIsProfileMenuOpen(false);
                      navigate('/profile');
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-300 hover:bg-slate-800/80 hover:text-white transition-colors flex items-center gap-2.5"
                  >
                    <UserIcon className="w-4 h-4 text-blue-400" />
                    <span>My Profile & Settings</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setIsProfileMenuOpen(false);
                      navigate('/feedback/new');
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-300 hover:bg-slate-800/80 hover:text-white transition-colors flex items-center gap-2.5"
                  >
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    <span>Submit New Feedback</span>
                  </button>

                  <div className="border-t border-slate-800/80 my-1" />

                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full text-left px-3 py-2 rounded-xl text-xs text-rose-400 hover:bg-rose-950/40 hover:text-rose-300 transition-colors flex items-center gap-2.5 font-semibold"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <NavLink
            to="/login"
            className="flex items-center gap-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300 px-3 py-1.5 rounded-xl bg-blue-600/10 border border-blue-500/30"
          >
            <UserIcon className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </NavLink>
        )}
      </div>
    </header>
  );
};
