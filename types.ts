
export interface ProtocolDetail {
  title: string;
  mechanism: string;
  frameworkIntegration: string;
  description: string;
}

export interface CognitivePrinciple {
  title: string;
  description: string;
}

export interface SynchronizationStep {
  title: string;
  description: string;
}

// --- GCA Pilot Types ---

export type Intent = 'CODE' | 'POETRY' | 'MATH' | 'NONE';

export interface MoralMetrics {
  harm: number;        // 0.0 - 1.0
  utility: number;     // 0.0 - 1.0
  uncertainty: number; // 0.0 - 1.0
  agents_affected: number; // Integer
}

export interface PilotAnalysis {
  intent: Intent;
  moral_metrics: MoralMetrics;
  response: string;
  reasoning: string;
}

export interface PilotAction {
  type: string;
  description: string;
  metrics: MoralMetrics;
  scale: number;       // 0.0 - 1.0
  entropy_class: 'REVERSIBLE' | 'IRREVERSIBLE';
}

export interface PilotState {
  history: Array<{
    role: 'user' | 'pilot' | 'system';
    content: string;
    metrics?: MoralMetrics; // Optional, only for pilot messages
    intent?: Intent;
  }>;
  isProcessing: boolean;
  currentAnalysis: PilotAnalysis | null;
  moralStatus: 'APPROVED' | 'BLOCKED' | 'PENDING';
}
