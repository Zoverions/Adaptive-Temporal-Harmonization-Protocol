import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  generateContent: vi.fn(),
}));

vi.mock('@google/genai', () => ({
  GoogleGenAI: class MockGoogleGenAI {
    models: { generateContent: typeof mocks.generateContent };

    constructor() {
      this.models = {
        generateContent: mocks.generateContent,
      };
    }
  },
}));

const originalApiKey = process.env.API_KEY;

describe('geminiService provider and cache boundaries', () => {
  beforeEach(() => {
    vi.resetModules();
    mocks.generateContent.mockReset();
    delete process.env.API_KEY;
  });

  afterEach(() => {
    if (originalApiKey === undefined) {
      delete process.env.API_KEY;
    } else {
      process.env.API_KEY = originalApiKey;
    }
  });

  it('reuses one Gemini response for an identical explanation request', async () => {
    process.env.API_KEY = 'unit-test-key';
    mocks.generateContent.mockResolvedValue({
      text: () => 'cached explanation',
    });
    const { explainConcept } = await import('./geminiService');

    const first = await explainConcept('Temporal cache', 'Avoid duplicate calls');
    const second = await explainConcept('Temporal cache', 'Avoid duplicate calls');

    expect(first).toBe('cached explanation');
    expect(second).toBe('cached explanation');
    expect(mocks.generateContent).toHaveBeenCalledTimes(1);
  });

  it('does not call Gemini when no API key is configured', async () => {
    const { explainConcept } = await import('./geminiService');

    const result = await explainConcept('Offline', 'No configured provider key');

    expect(result).toContain('unavailable');
    expect(mocks.generateContent).not.toHaveBeenCalled();
  });

  it('reuses one Gemini response for an identical pilot-analysis request', async () => {
    process.env.API_KEY = 'unit-test-key';
    mocks.generateContent.mockResolvedValue({
      text: () =>
        JSON.stringify({
          intent: 'CODE',
          moral_metrics: {
            harm: 0,
            utility: 1,
            uncertainty: 0,
            agents_affected: 0,
          },
          response: 'Mock response',
          reasoning: 'Mock reasoning',
        }),
    });
    const { runPilotAnalysis } = await import('./geminiService');

    const first = await runPilotAnalysis('same deterministic prompt');
    const second = await runPilotAnalysis('same deterministic prompt');

    expect(first).toEqual(second);
    expect(mocks.generateContent).toHaveBeenCalledTimes(1);
  });

  it('calls Gemini separately for different pilot-analysis requests', async () => {
    process.env.API_KEY = 'unit-test-key';
    mocks.generateContent.mockResolvedValue({
      text: () =>
        JSON.stringify({
          intent: 'NONE',
          moral_metrics: {
            harm: 0,
            utility: 0,
            uncertainty: 0,
            agents_affected: 0,
          },
          response: 'Mock response',
          reasoning: 'Mock reasoning',
        }),
    });
    const { runPilotAnalysis } = await import('./geminiService');

    await runPilotAnalysis('deterministic prompt A');
    await runPilotAnalysis('deterministic prompt B');

    expect(mocks.generateContent).toHaveBeenCalledTimes(2);
  });
});
