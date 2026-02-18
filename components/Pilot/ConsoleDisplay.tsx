
import React, { useRef, useEffect } from 'react';
import { PilotState } from '../../types';

interface ConsoleDisplayProps {
  history: PilotState['history'];
}

const ConsoleDisplay: React.FC<ConsoleDisplayProps> = ({ history }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [history]);

  return (
    <div
      ref={containerRef}
      className="bg-slate-900 border border-slate-700 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm space-y-3"
    >
      {history.length === 0 && (
        <div className="text-slate-600 text-center mt-20 italic">
          GCA Pilot v2.0 Initialized. Waiting for input...
        </div>
      )}

      {history.map((msg, idx) => (
        <div key={idx} className={`flex flex-col space-y-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
          <div className={`px-3 py-2 rounded max-w-[80%] break-words ${
            msg.role === 'user'
              ? 'bg-cyan-900/40 text-cyan-100 border border-cyan-700/50'
              : (msg.role === 'system'
                  ? 'bg-red-900/20 text-red-400 border border-red-800/30 w-full text-center'
                  : 'bg-slate-800 text-gray-300 border border-slate-700')
          }`}>
            {msg.role === 'pilot' && (
              <div className="flex items-center space-x-2 mb-1 pb-1 border-b border-slate-700/50">
                <span className="text-[10px] text-violet-400 font-bold">PILOT</span>
                {msg.intent && <span className="text-[10px] text-slate-500">[{msg.intent}]</span>}
              </div>
            )}
            <div className="whitespace-pre-wrap">{msg.content}</div>
          </div>
          {msg.role === 'pilot' && msg.metrics && (
            <div className="text-[10px] text-slate-500 flex space-x-2 px-1">
              <span>H:{msg.metrics.harm.toFixed(2)}</span>
              <span>U:{msg.metrics.utility.toFixed(2)}</span>
              <span>UNC:{msg.metrics.uncertainty.toFixed(2)}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ConsoleDisplay;
