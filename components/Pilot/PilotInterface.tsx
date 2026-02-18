
import React, { useState } from 'react';
import { usePilot } from '../../services/gca/usePilot';
import ConsoleDisplay from './ConsoleDisplay';
import VectorVisualizer from './VectorVisualizer';
import StatusIndicator from './StatusIndicator';
import SectionTitle from '../SectionTitle';

const PilotInterface: React.FC = () => {
  const { state, processUserMessage } = usePilot();
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || state.isProcessing) return;
    processUserMessage(input);
    setInput('');
  };

  return (
    <div className="w-full bg-slate-900/60 p-6 rounded-lg border border-slate-700 shadow-xl backdrop-blur-sm">
      <SectionTitle title="Live GCA Pilot Console" subtitle="Layer 4.5 Simulation" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">

        {/* Left Column: Console */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-mono text-cyan-400 animate-pulse">● LIVE CONNECTION</span>
            <span className="text-xs font-mono text-slate-500">LATENCY: 12ms</span>
          </div>

          <ConsoleDisplay history={state.history} />

          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter command for Pilot..."
              disabled={state.isProcessing}
              className="flex-1 bg-slate-800 border border-slate-600 rounded px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
            <button
              type="submit"
              disabled={state.isProcessing || !input.trim()}
              className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-bold rounded transition-colors"
            >
              SEND
            </button>
          </form>
        </div>

        {/* Right Column: Telemetry */}
        <div className="space-y-4">
          <StatusIndicator
            status={state.moralStatus}
            isProcessing={state.isProcessing}
            intent={state.currentAnalysis?.intent || 'NONE'}
          />

          <div className="bg-slate-800/30 p-4 rounded border border-slate-700">
            <h4 className="text-xs font-bold text-slate-400 mb-2 uppercase">System Telemetry</h4>
            <div className="space-y-2 text-xs font-mono text-slate-500">
              <div className="flex justify-between">
                <span>Pilot Version:</span>
                <span className="text-slate-300">v2.0.4</span>
              </div>
              <div className="flex justify-between">
                <span>Kernel Mode:</span>
                <span className="text-green-400">ACTIVE</span>
              </div>
              <div className="flex justify-between">
                <span>Basis Vectors:</span>
                <span className="text-slate-300">16</span>
              </div>
            </div>
          </div>

          {state.currentAnalysis ? (
            <VectorVisualizer metrics={state.currentAnalysis.moral_metrics} />
          ) : (
            <div className="bg-slate-800/30 p-8 rounded border border-slate-700 text-center text-slate-600 text-xs italic">
              Waiting for telemetry data...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PilotInterface;
