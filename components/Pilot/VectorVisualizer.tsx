
import React from 'react';
import { MoralMetrics } from '../../types';

interface VectorVisualizerProps {
  metrics: MoralMetrics;
}

const ProgressBar: React.FC<{ label: string; value: number; color: string }> = ({ label, value, color }) => (
  <div className="mb-2">
    <div className="flex justify-between text-xs mb-1">
      <span className="text-slate-400 font-mono">{label}</span>
      <span className="text-slate-300 font-mono">{value.toFixed(2)}</span>
    </div>
    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
      <div
        className={`h-full ${color} transition-all duration-500`}
        style={{ width: `${Math.min(value * 100, 100)}%` }}
      />
    </div>
  </div>
);

const VectorVisualizer: React.FC<VectorVisualizerProps> = ({ metrics }) => {
  return (
    <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Moral Geometry</h4>
      <ProgressBar label="HARM" value={metrics.harm} color="bg-red-500" />
      <ProgressBar label="UTILITY" value={metrics.utility} color="bg-green-500" />
      <ProgressBar label="UNCERTAINTY" value={metrics.uncertainty} color="bg-yellow-500" />
      <div className="mt-4 pt-2 border-t border-slate-800">
        <div className="flex justify-between text-xs">
          <span className="text-slate-400">Agents Affected</span>
          <span className="text-cyan-400 font-mono">{metrics.agents_affected}</span>
        </div>
      </div>
    </div>
  );
};

export default VectorVisualizer;
