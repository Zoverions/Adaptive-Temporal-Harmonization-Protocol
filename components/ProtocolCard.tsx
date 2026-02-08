
import React, { useState, useCallback } from 'react';
import { ProtocolDetail } from '../types';
import { explainConcept } from '../services/geminiService';

interface ProtocolCardProps {
  protocol: ProtocolDetail;
}

const ProtocolCard: React.FC<ProtocolCardProps> = ({ protocol }) => {
  const [explanation, setExplanation] = useState<string>('');
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleExplain = useCallback(() => {
    if (isVisible) {
      setIsVisible(false); // Toggle to hide
      return;
    }

    if (explanation) {
      setIsVisible(true); // Show cached explanation
      return;
    }

    setIsLoading(true);
    explainConcept(protocol.title, protocol.description)
      .then((res) => {
        setExplanation(res);
        setIsVisible(true);
      })
      .finally(() => setIsLoading(false));
  }, [protocol.title, protocol.description, explanation, isVisible]);

  return (
    <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700 flex flex-col h-full group hover:border-violet-500/70 transition-all duration-300">
      <div className="flex-grow">
        <h3 className="text-xl font-bold text-violet-400 group-hover:text-violet-300 transition-colors">{protocol.title}</h3>
        <p className="text-sm mt-2 text-slate-300">{protocol.description}</p>
        <p className="text-sm mt-4 font-mono border-l-2 border-slate-600 pl-3 text-slate-400">{protocol.mechanism}</p>
      </div>
      
      <div className="mt-4">
        <button 
          onClick={handleExplain}
          disabled={isLoading}
          className="w-full text-sm font-semibold text-cyan-300 bg-cyan-900/50 hover:bg-cyan-800/50 border border-cyan-700/50 rounded-md px-4 py-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Thinking...' : (isVisible ? 'Hide AI Explanation' : 'Explain with AI')}
        </button>
        {isVisible && explanation && !isLoading && (
          <div className="mt-4 p-3 bg-slate-900/70 rounded-md border border-slate-600">
            <p className="text-sm text-gray-200">{explanation}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProtocolCard;
