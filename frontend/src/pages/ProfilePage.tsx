import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import type { User } from '../types';
import { CustomDropdown } from '../components/common/CustomDropdown';
import { Badge } from '../components/common/Badge';
import {
  User as UserIcon,
  Mail,
  Shield,
  KeyRound,
  Eye,
  EyeOff,
  CheckCircle2,
  Save,
  Calendar,
  Lock,
  Activity,
  Moon,
  Sun,
  Zap,
  Sparkles
} from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user, updateProfile } = useAuth();
  const { theme, setTheme } = useTheme();

  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [role, setRole] = useState<User['role']>(user?.role || 'Product Manager');

  // Password Visibility Toggle State
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [profileSuccessMsg, setProfileSuccessMsg] = useState<string | null>(null);
  const [passwordSuccessMsg, setPasswordSuccessMsg] = useState<string | null>(null);
  const [passwordErrorMsg, setPasswordErrorMsg] = useState<string | null>(null);

  if (!user) return null;

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile({ name, email, role });
    setProfileSuccessMsg('Profile information updated successfully.');
    setTimeout(() => setProfileSuccessMsg(null), 4000);
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordErrorMsg(null);
    setPasswordSuccessMsg(null);

    if (newPassword.length < 6) {
      setPasswordErrorMsg('New password must be at least 6 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordErrorMsg('New password and confirm password do not match.');
      return;
    }

    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setPasswordSuccessMsg('Security password updated successfully.');
    setTimeout(() => setPasswordSuccessMsg(null), 4000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header Banner */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 md:p-8 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center text-white font-extrabold text-2xl shadow-lg border-2 border-slate-700">
            {user.avatar || 'U'}
          </div>
          <div className="space-y-1">
            <h1 className="text-2xl font-bold text-white tracking-tight">{user.name}</h1>
            <p className="text-xs text-slate-400 font-mono">{user.email}</p>
            <div className="pt-1 flex items-center justify-center sm:justify-start gap-2">
              <Badge variant="brand">{user.role}</Badge>
              <span className="text-[11px] text-slate-500 flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-500" />
                Joined August 2026
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Settings Forms */}
        <div className="lg:col-span-2 space-y-8">
          {/* Section 1: Edit Profile */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 shadow-sm space-y-6">
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
              <UserIcon className="w-4 h-4" />
              <span>Personal Profile Information</span>
            </div>

            {profileSuccessMsg && (
              <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{profileSuccessMsg}</span>
              </div>
            )}

            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                  Display Name
                </label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 text-slate-100 text-xs rounded-lg pl-9 pr-4 py-2.5 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 text-slate-100 text-xs rounded-lg pl-9 pr-4 py-2.5 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <CustomDropdown
                  label="Account Role"
                  value={role}
                  options={[
                    { value: 'Product Manager', label: 'Product Manager' },
                    { value: 'Lead Engineer', label: 'Lead Engineer' },
                    { value: 'QA Lead', label: 'QA Lead' },
                    { value: 'Administrator', label: 'Administrator' },
                  ]}
                  onChange={(val) => setRole(val as User['role'])}
                />
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-2 shadow-sm"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>Save Profile</span>
                </button>
              </div>
            </form>
          </div>

          {/* Section 2: Security & Password with Password Visibility Toggle */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 shadow-sm space-y-6">
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
              <KeyRound className="w-4 h-4" />
              <span>Password & Security Settings</span>
            </div>

            {passwordSuccessMsg && (
              <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{passwordSuccessMsg}</span>
              </div>
            )}

            {passwordErrorMsg && (
              <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs">
                <span>{passwordErrorMsg}</span>
              </div>
            )}

            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              {/* Current Password */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                  Current Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type={showCurrentPassword ? 'text' : 'password'}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-slate-900 border border-slate-700 text-slate-100 text-xs rounded-lg pl-9 pr-10 py-2.5 focus:border-blue-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                    title={showCurrentPassword ? 'Hide password' : 'Show password'}
                  >
                    {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* New Password */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-slate-900 border border-slate-700 text-slate-100 text-xs rounded-lg pl-9 pr-10 py-2.5 focus:border-blue-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                    title={showNewPassword ? 'Hide password' : 'Show password'}
                  >
                    {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-slate-900 border border-slate-700 text-slate-100 text-xs rounded-lg pl-9 pr-10 py-2.5 focus:border-blue-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                    title={showConfirmPassword ? 'Hide password' : 'Show password'}
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="submit"
                  disabled={!newPassword}
                  className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-2 shadow-sm"
                >
                  <KeyRound className="w-3.5 h-3.5" />
                  <span>Update Password</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right 1 Col: Permissions, Theme & Activity */}
        <div className="space-y-6">
          {/* Theme Preferences Card */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-purple-400 uppercase tracking-wider">
              <Sparkles className="w-4 h-4" />
              <span>Theme & Style Preference</span>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setTheme('dark')}
                className={`p-2.5 rounded-xl border text-center transition-all ${
                  theme === 'dark'
                    ? 'bg-blue-600/20 border-blue-500 text-white font-bold shadow-sm'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Moon className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                <span className="block text-[10px]">Dark</span>
              </button>

              <button
                type="button"
                onClick={() => setTheme('cyber')}
                className={`p-2.5 rounded-xl border text-center transition-all ${
                  theme === 'cyber'
                    ? 'bg-cyan-600/20 border-cyan-500 text-white font-bold shadow-sm'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Zap className="w-4 h-4 mx-auto mb-1 text-cyan-400 animate-pulse" />
                <span className="block text-[10px]">Cyber</span>
              </button>

              <button
                type="button"
                onClick={() => setTheme('light')}
                className={`p-2.5 rounded-xl border text-center transition-all ${
                  theme === 'light'
                    ? 'bg-amber-600/20 border-amber-500 text-white font-bold shadow-sm'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Sun className="w-4 h-4 mx-auto mb-1 text-amber-400" />
                <span className="block text-[10px]">Light</span>
              </button>
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
              <Shield className="w-4 h-4" />
              <span>Role Permissions</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded-lg border border-slate-800">
                <span className="text-slate-300">Submit & Analyze Feedback</span>
                <span className="text-emerald-400 font-bold">Allowed</span>
              </div>
              <div className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded-lg border border-slate-800">
                <span className="text-slate-300">Generate Roadmaps</span>
                <span className="text-emerald-400 font-bold">Allowed</span>
              </div>
              <div className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded-lg border border-slate-800">
                <span className="text-slate-300">Update Developer Tasks</span>
                <span className="text-emerald-400 font-bold">Allowed</span>
              </div>
              <div className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded-lg border border-slate-800">
                <span className="text-slate-300">System Admin Access</span>
                <span className="text-slate-400 font-semibold">{user.role === 'Administrator' ? 'Full' : 'Standard'}</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
              <Activity className="w-4 h-4" />
              <span>Session Overview</span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center text-slate-400">
                <span>Active Model:</span>
                <span className="font-mono text-slate-200">llama3.1</span>
              </div>
              <div className="flex justify-between items-center text-slate-400">
                <span>API Endpoint:</span>
                <span className="font-mono text-slate-200">http://127.0.0.1:8000</span>
              </div>
              <div className="flex justify-between items-center text-slate-400">
                <span>User ID:</span>
                <span className="font-mono text-slate-200 text-[11px] truncate max-w-[120px]">{user.id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
