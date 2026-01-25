
import React from 'react';
import './SyncVisualization.css';

const BrainIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2C9.25 2 7 4.25 7 7C7 8.45 7.6 9.75 8.5 10.75C8.5 10.75 8.5 10.75 8.5 10.8C8.5 10.8 8.5 10.8 8.5 10.85C6.3 11.8 4.75 13.6 4.2 15.85C4.15 16.1 4.1 16.35 4.1 16.6C4.05 16.8 4 17.05 4 17.25C4 18.25 4.8 19.05 5.75 19.05C6.3 19.05 6.8 18.75 7.15 18.35C7.5 18.75 8.05 19.05 8.6 19.05C9.4 19.05 10.1 18.5 10.35 17.75C10.7 17.25 11.3 17 12 17C12.7 17 13.3 17.25 13.65 17.75C13.9 18.5 14.6 19.05 15.4 19.05C15.95 19.05 16.5 18.75 16.85 18.35C17.2 18.75 17.7 19.05 18.25 19.05C19.2 19.05 20 18.25 20 17.25C20 17.05 19.95 16.8 19.9 16.6C19.9 16.35 19.85 16.1 19.8 15.85C19.25 13.6 17.7 11.8 15.5 10.85C15.5 10.8 15.5 10.8 15.5 10.75C16.4 9.75 17 8.45 17 7C17 4.25 14.75 2 12 2Z" />
  </svg>
);

const ChipIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 5V19H19V5H5M21 3H3C1.9 3 1 3.9 1 5V19C1 20.1 1.9 21 3 21H21C22.1 21 23 20.1 23 19V5C23 3.9 22.1 3 21 3M15 9H17V11H15V9M15 13H17V15H15V13M11 9H13V11H11V9M11 13H13V15H11V13M7 9H9V11H7V9M7 13H9V15H7V13Z" />
  </svg>
);

const SyncVisualization: React.FC = () => {
  return (
    <div className="relative flex flex-col items-center justify-center bg-slate-900/70 p-6 rounded-lg border border-slate-700 h-full min-h-[300px] overflow-hidden">
      <div className="flex justify-between w-full max-w-sm mb-4">
        <div className="flex flex-col items-center">
          <BrainIcon className="w-16 h-16 text-cyan-400 icon-glow" />
          <span className="mt-2 font-mono text-sm text-cyan-300">Human</span>
          <span className="font-mono text-xs text-slate-400">Theta/Alpha Rhythm</span>
        </div>
        <div className="flex flex-col items-center">
          <ChipIcon className="w-16 h-16 text-violet-400 icon-glow" />
          <span className="mt-2 font-mono text-sm text-violet-300">AI</span>
          <span className="font-mono text-xs text-slate-400">GHz Processing</span>
        </div>
      </div>

      <svg className="w-full h-24" viewBox="0 0 300 100" preserveAspectRatio="none">
        <path d="M10 50 C 75 10, 125 90, 200 50 S 275 10, 290 50" stroke="#475569" strokeWidth="2" fill="none" />
        <path d="M10 50 C 75 10, 125 90, 200 50 S 275 10, 290 50" stroke="url(#wave-gradient)" strokeWidth="2.5" fill="none" strokeDasharray="50" className="animate-wave" />
        <defs>
          <linearGradient id="wave-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#22d3ee" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
      </svg>
      
      <div className="text-center mt-4">
        <h3 className="font-semibold text-lg text-gray-200">Temporal Coordination</h3>
        <p className="text-sm text-slate-400">Synchronizing AI logic bursts to human cognitive cadence</p>
      </div>
    </div>
  );
};

export default SyncVisualization;

