import React from 'react';
import LoadingSpinner from './LoadingSpinner';

export default function ChartCard({ title, description, loading, children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {(title || description) && (
        <div className="mb-4">
          {title && <h3 className="section-title">{title}</h3>}
          {description && <p className="text-sm text-slate-500 mt-1">{description}</p>}
        </div>
      )}
      {loading ? (
        <LoadingSpinner message="Loading chart..." size="sm" />
      ) : (
        children
      )}
    </div>
  );
}
