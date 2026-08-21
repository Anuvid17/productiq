import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'neutral' | 'brand' | 'success' | 'warning' | 'danger' | 'purple';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'sm',
  className = '',
}) => {
  const variantStyles = {
    neutral: 'bg-slate-800 text-slate-300 border-slate-700',
    brand: 'bg-blue-950/70 text-blue-400 border-blue-800/60',
    success: 'bg-emerald-950/70 text-emerald-400 border-emerald-800/60',
    warning: 'bg-amber-950/70 text-amber-400 border-amber-800/60',
    danger: 'bg-rose-950/70 text-rose-400 border-rose-800/60',
    purple: 'bg-purple-950/70 text-purple-400 border-purple-800/60',
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center font-medium border rounded-md uppercase tracking-wider ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </span>
  );
};

export const PriorityBadge: React.FC<{ priority?: string }> = ({ priority }) => {
  if (!priority) return null;
  const p = priority.toUpperCase();
  let variant: 'danger' | 'warning' | 'brand' | 'neutral' = 'neutral';
  if (p === 'P0') variant = 'danger';
  else if (p === 'P1') variant = 'warning';
  else if (p === 'P2') variant = 'brand';

  return <Badge variant={variant}>{priority}</Badge>;
};

export const SeverityBadge: React.FC<{ severity?: string }> = ({ severity }) => {
  if (!severity) return null;
  const s = severity.toLowerCase();
  let variant: 'danger' | 'warning' | 'brand' | 'neutral' = 'neutral';
  if (s === 'blocker' || s === 'critical') variant = 'danger';
  else if (s === 'major') variant = 'warning';
  else if (s === 'minor') variant = 'brand';

  return <Badge variant={variant}>{severity}</Badge>;
};

export const StatusBadge: React.FC<{ status?: string }> = ({ status }) => {
  if (!status) return null;
  const s = status.toLowerCase();
  let variant: 'success' | 'warning' | 'brand' | 'purple' | 'neutral' = 'neutral';

  if (s === 'resolved' || s === 'released' || s === 'closed') variant = 'success';
  else if (s === 'in progress' || s === 'testing' || s === 'in review') variant = 'warning';
  else if (s === 'triaged' || s === 'approved' || s === 'planned') variant = 'brand';
  else if (s === 'open' || s === 'backlog') variant = 'neutral';

  return <Badge variant={variant}>{status}</Badge>;
};

export const ActionBadge: React.FC<{ action?: string }> = ({ action }) => {
  if (!action) return null;
  return <Badge variant="purple">{action.replace('_', ' ')}</Badge>;
};
