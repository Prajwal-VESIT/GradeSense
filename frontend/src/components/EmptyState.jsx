import React from 'react';
import { Inbox } from 'lucide-react';

export default function EmptyState({ icon: Icon = Inbox, title = 'No data', description = 'There is nothing to display right now.' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4 text-center animate-fade-in">
      <div className="p-4 rounded-full bg-slate-100">
        <Icon className="w-10 h-10 text-slate-400" />
      </div>
      <div>
        <h3 className="text-lg font-semibold text-slate-700">{title}</h3>
        <p className="text-sm text-slate-500 mt-1 max-w-sm">{description}</p>
      </div>
    </div>
  );
}
