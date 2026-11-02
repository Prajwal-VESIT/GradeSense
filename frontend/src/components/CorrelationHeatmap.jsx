import React, { useState, useMemo } from 'react';

function getColor(value) {
  // Blue (negative) → White (zero) → Red (positive)
  const v = Math.max(-1, Math.min(1, value));
  if (v >= 0) {
    const intensity = Math.round(v * 200);
    return `rgb(${155 + intensity * 0.5}, ${50 + (1 - v) * 150}, ${50 + (1 - v) * 150})`;
  } else {
    const intensity = Math.round(Math.abs(v) * 200);
    return `rgb(${50 + (1 - Math.abs(v)) * 150}, ${50 + (1 - Math.abs(v)) * 150}, ${155 + intensity * 0.5})`;
  }
}

function getCellColor(value) {
  const v = Math.max(-1, Math.min(1, value));
  if (v >= 0) {
    const r = Math.round(255 - v * 127);
    const g = Math.round(255 - v * 80);
    const b = Math.round(255 - v * 80);
    const rText = Math.round(v * 220);
    return {
      bg: `rgb(${r}, ${g > 50 ? g : 50}, ${b > 50 ? b : 50})`,
      text: v > 0.4 ? '#fff' : '#334155',
      bgActual: v > 0.4
        ? `rgb(${Math.round(220 * v)}, ${Math.round(60 * (1 - v) + 40)}, ${Math.round(60 * (1 - v) + 40)})`
        : `rgb(255, ${Math.round(255 - v * 180)}, ${Math.round(255 - v * 180)})`,
    };
  } else {
    const absV = Math.abs(v);
    return {
      bg: absV > 0.4
        ? `rgb(${Math.round(60 * (1 - absV) + 40)}, ${Math.round(60 * (1 - absV) + 40)}, ${Math.round(220 * absV)})`
        : `rgb(${Math.round(255 - absV * 180)}, ${Math.round(255 - absV * 180)}, 255)`,
      text: absV > 0.4 ? '#fff' : '#334155',
    };
  }
}

export default function CorrelationHeatmap({ features, correlationMatrix }) {
  const [hoveredCell, setHoveredCell] = useState(null);

  const displayFeatures = useMemo(() => {
    if (!features || features.length === 0) return [];
    // If too many features, show a subset
    if (features.length > 15) {
      return features.slice(0, 15);
    }
    return features;
  }, [features]);

  const displayMatrix = useMemo(() => {
    if (!correlationMatrix || correlationMatrix.length === 0) return [];
    const len = displayFeatures.length;
    return correlationMatrix.slice(0, len).map((row) => row.slice(0, len));
  }, [correlationMatrix, displayFeatures]);

  if (!displayFeatures.length || !displayMatrix.length) {
    return <p className="text-sm text-slate-500">No correlation data available.</p>;
  }

  const n = displayFeatures.length;
  const cellSize = n > 12 ? 36 : 44;

  return (
    <div className="overflow-x-auto">
      <div className="inline-block">
        {/* Column labels */}
        <div className="flex" style={{ marginLeft: cellSize * 2.5 }}>
          {displayFeatures.map((f, i) => (
            <div
              key={i}
              className="text-[10px] text-slate-600 font-medium overflow-hidden"
              style={{
                width: cellSize,
                height: cellSize * 2,
                writingMode: 'vertical-rl',
                transform: 'rotate(180deg)',
                textAlign: 'left',
                lineHeight: `${cellSize}px`,
              }}
            >
              {f}
            </div>
          ))}
        </div>

        {/* Rows */}
        {displayMatrix.map((row, i) => (
          <div key={i} className="flex items-center">
            {/* Row label */}
            <div
              className="text-[10px] text-slate-600 font-medium text-right pr-2 truncate flex-shrink-0"
              style={{ width: cellSize * 2.5 }}
            >
              {displayFeatures[i]}
            </div>
            {/* Cells */}
            {row.map((val, j) => {
              const style = getCellColor(val);
              const isHovered =
                hoveredCell && hoveredCell.row === i && hoveredCell.col === j;
              return (
                <div
                  key={j}
                  className={`flex items-center justify-center border border-white/50 cursor-pointer transition-all duration-100 ${
                    isHovered ? 'ring-2 ring-slate-800 z-10' : ''
                  }`}
                  style={{
                    width: cellSize,
                    height: cellSize,
                    backgroundColor: style.bgActual || style.bg,
                    color: style.text,
                    fontSize: n > 12 ? '8px' : '10px',
                    fontWeight: 500,
                  }}
                  onMouseEnter={() => setHoveredCell({ row: i, col: j, value: val })}
                  onMouseLeave={() => setHoveredCell(null)}
                  title={`${displayFeatures[i]} × ${displayFeatures[j]}: ${val?.toFixed(3)}`}
                >
                  {n <= 10 ? val?.toFixed(2) : (isHovered ? val?.toFixed(2) : '')}
                </div>
              );
            })}
          </div>
        ))}

        {/* Legend */}
        <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
          <span>-1</span>
          <div className="flex h-4 rounded overflow-hidden" style={{ width: 200 }}>
            {Array.from({ length: 20 }, (_, i) => {
              const v = -1 + (i / 19) * 2;
              const s = getCellColor(v);
              return (
                <div
                  key={i}
                  className="flex-1"
                  style={{ backgroundColor: s.bgActual || s.bg }}
                />
              );
            })}
          </div>
          <span>+1</span>
          <span className="ml-2 text-slate-400">Correlation</span>
        </div>

        {/* Tooltip */}
        {hoveredCell && (
          <div className="mt-2 text-sm text-slate-700">
            <span className="font-medium">{displayFeatures[hoveredCell.row]}</span>
            {' × '}
            <span className="font-medium">{displayFeatures[hoveredCell.col]}</span>
            {': '}
            <span className="font-bold">{hoveredCell.value?.toFixed(4)}</span>
          </div>
        )}
      </div>

      {features && features.length > 15 && (
        <p className="text-xs text-slate-400 mt-2">
          Showing top 15 of {features.length} features. Full matrix available via API.
        </p>
      )}
    </div>
  );
}
