import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function ErrorAlert({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4 animate-fade-in">
      <div className="p-3 rounded-full bg-rose-100">
        <AlertTriangle className="w-8 h-8 text-rose-600" />
      </div>
      <div className="text-center">
        <h3 className="text-lg font-semibold text-slate-900">Something went wrong</h3>
        <p className="text-sm text-slate-500 mt-1 max-w-md">
          {message || 'An unexpected error occurred. Please try again.'}
        </p>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Try Again
        </button>
      )}
    </div>
  );
}
