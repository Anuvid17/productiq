import React from 'react';

interface ProgressBarProps {
  progress: number;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  showText = true,
  size = 'md',
  className = '',
}) => {
  const clampedProgress = Math.max(0, Math.min(100, Math.round(progress)));

  let colorClass = 'bg-blue-500';
  if (clampedProgress === 100) {
    colorClass = 'bg-emerald-500';
  } else if (clampedProgress >= 50) {
    colorClass = 'bg-blue-500';
  } else if (clampedProgress > 0) {
    colorClass = 'bg-amber-500';
  }

  const heightClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  };

  return (
    <div className={`w-full ${className}`}>
      <div className="flex items-center justify-between mb-1">
        {showText && (
          <span className="text-xs font-semibold text-slate-300">
            {clampedProgress}% Complete
          </span>
        )}
      </div>
      <div className={`w-full bg-slate-800 rounded-full overflow-hidden ${heightClasses[size]}`}>
        <div
          className={`${colorClass} ${heightClasses[size]} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${clampedProgress}%` }}
        />
      </div>
    </div>
  );
};
