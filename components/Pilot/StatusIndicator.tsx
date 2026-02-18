
import React from 'react';

interface StatusIndicatorProps {
  status: 'APPROVED' | 'BLOCKED' | 'PENDING';
  isProcessing: boolean;
  intent: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, isProcessing, intent }) => {
  const getStatusColor = () => {
    if (isProcessing) return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/50';
    if (status === 'APPROVED') return 'bg-green-500/20 text-green-500 border-green-500/50';
    if (status === 'BLOCKED') return 'bg-red-500/20 text-red-500 border-red-500/50';
    return 'bg-slate-800 text-slate-400 border-slate-700';
  };

  const getStatusText = () => {
    if (isProcessing) return 'PROCESSING...';
    if (status === 'APPROVED') return 'SYSTEMS NORMAL';
    if (status === 'BLOCKED') return 'INTERVENTION REQUIRED';
    return 'STANDBY';
  };

  return (
    <div className={`flex items-center justify-between p-3 rounded border ${getStatusColor()} transition-colors duration-300`}>
      <div className="flex items-center space-x-3">
        <div className={`w-2 h-2 rounded-full ${isProcessing ? 'animate-pulse bg-yellow-500' : (status === 'APPROVED' ? 'bg-green-500' : (status === 'BLOCKED' ? 'bg-red-500' : 'bg-slate-500'))}`} />
        <span className="font-mono text-sm font-bold tracking-wider">{getStatusText()}</span>
      </div>
      <div className="flex items-center space-x-2">
        <span className="text-xs text-slate-500 uppercase tracking-wider">Current Intent:</span>
        <span className="font-mono text-xs font-bold text-cyan-400">{intent || 'NONE'}</span>
      </div>
    </div>
  );
};

export default StatusIndicator;
