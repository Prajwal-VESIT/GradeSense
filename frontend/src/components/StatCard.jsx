import React from 'react';

export default function StatCard({ icon: Icon, label, value, subtitle, trend, className = '' }) {
  return (
    <div className={`card-hover flex items-start gap-4 ${className}`}>
      {Icon && (
        <div className="flex-shrink-0 p-3 rounded-lg bg-primary-50 text-primary-600">
          <Icon className="w-5 h-5" />
        </div>
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-500 truncate">{label}</p>
        <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
        {subtitle && (
          <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
        )}
        {trend !== undefined && trend !== null && (
          <div className={`flex items-center gap-1 mt-1 text-xs font-medium ${
            trend >= 0 ? 'text-emerald-600' : 'text-rose-600'
          }`}>
            <span>{trend >= 0 ? '↑' : '↓'}</span>
            <span>{Math.abs(trend)}</span>
          </div>
        )}
      </div>
    </div>
  );
}
