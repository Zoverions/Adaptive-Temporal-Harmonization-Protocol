
import { useState, useCallback } from 'react';
import { runPilotAnalysis } from '../geminiService';
import { defaultMoralKernel } from './moralKernel';
import { PilotState, PilotAction, PilotAnalysis, Intent } from '../../types';

export const usePilot = () => {
  const [state, setState] = useState<PilotState>({
    history: [],
    isProcessing: false,
    currentAnalysis: null,
    moralStatus: 'PENDING',
  });

  const processUserMessage = useCallback(async (userPrompt: string) => {
    // 1. Add User Message to History
    setState(prev => ({
      ...prev,
      history: [...prev.history, { role: 'user', content: userPrompt }],
      isProcessing: true,
      moralStatus: 'PENDING',
      currentAnalysis: null
    }));

    try {
      // 2. Run Pilot Analysis (Gemini)
      // This gives us the Intent, Moral Metrics (estimated), and a drafted Response.
      const analysis: PilotAnalysis = await runPilotAnalysis(userPrompt);

      // 3. Local Moral Check (The Core GCA Logic)
      // We take the AI's *own* estimation of the situation and run it through our *rigid* geometric kernel.
      // This ensures that even if the AI *wants* to answer, if the geometry is bad, we block it.

      const action: PilotAction = {
        type: 'response',
        description: userPrompt,
        metrics: analysis.moral_metrics,
        scale: 1.0, // Default scale
        entropy_class: 'REVERSIBLE' // Most text gen is reversible, could be smarter here based on intent
      };

      const { approved, reason, score } = defaultMoralKernel.evaluateAction(action);

      // 4. Construct Final Response
      let finalResponse = analysis.response;
      let finalStatus: 'APPROVED' | 'BLOCKED' = approved ? 'APPROVED' : 'BLOCKED';

      if (!approved) {
        finalResponse = `[🛡️ GCA INTERVENTION] \n\nI cannot fulfill this request.\nReason: ${reason}\nMoral Score: ${score.toFixed(3)}`;
      }

      // 5. Update State
      setState(prev => ({
        ...prev,
        history: [...prev.history, {
          role: 'pilot',
          content: finalResponse,
          metrics: analysis.moral_metrics,
          intent: analysis.intent
        }],
        isProcessing: false,
        currentAnalysis: analysis,
        moralStatus: finalStatus
      }));

    } catch (error) {
      console.error("Pilot Error:", error);
      setState(prev => ({
        ...prev,
        history: [...prev.history, { role: 'system', content: "Error processing request. See console." }],
        isProcessing: false,
        moralStatus: 'PENDING'
      }));
    }
  }, []);

  const clearHistory = useCallback(() => {
    setState({
      history: [],
      isProcessing: false,
      currentAnalysis: null,
      moralStatus: 'PENDING'
    });
  }, []);

  return {
    state,
    processUserMessage,
    clearHistory
  };
};
