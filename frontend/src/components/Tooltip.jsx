import React, { useState } from 'react';
import { Info } from 'lucide-react';

export default function Tooltip({ text, children }) {
  const [show, setShow] = useState(false);

  if (!text) return children || null;

  return (
    <span
      className="relative inline-flex items-center"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      {children || <Info className="w-4 h-4 text-slate-400 cursor-help" />}
      {show && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 text-xs text-white bg-slate-800 rounded-lg shadow-lg whitespace-normal w-64 z-50 animate-fade-in pointer-events-none">
          {text}
          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-800" />
        </span>
      )}
    </span>
  );
}
