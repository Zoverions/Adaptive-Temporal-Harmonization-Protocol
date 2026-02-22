import { describe, it, expect, vi, beforeEach } from 'vitest';
import { runPilotAnalysis } from './geminiService';

const mocks = vi.hoisted(() => {
  return {
    generateContent: vi.fn().mockImplementation(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
      return {
        text: () => JSON.stringify({
          intent: 'CODE',
          moral_metrics: { harm: 0, utility: 1, uncertainty: 0, agents_affected: 0 },
          response: 'Mock response',
          reasoning: 'Mock reasoning'
        })
      };
    })
  };
});

vi.mock('@google/genai', () => {
  return {
    GoogleGenAI: class {
      models: any;
      constructor() {
        this.models = {
          generateContent: mocks.generateContent
        };
      }
    }
  };
});

describe('runPilotAnalysis Performance', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.API_KEY = 'test_key';
  });

  it('should call API only once for duplicate inputs (optimized behavior)', async () => {
    const prompt = 'Analyze this unique code ' + Math.random();

    const start = performance.now();
    await runPilotAnalysis(prompt); // Cache Miss -> API Call (100ms)
    await runPilotAnalysis(prompt); // Cache Hit -> Instant
    const end = performance.now();

    const duration = end - start;
    console.log(`Total duration for 2 identical calls: ${duration.toFixed(2)}ms`);

    expect(mocks.generateContent).toHaveBeenCalledTimes(1);
    expect(duration).toBeLessThan(180);
  });

  it('should call API again for different inputs', async () => {
    const prompt1 = 'Prompt A ' + Math.random();
    const prompt2 = 'Prompt B ' + Math.random();

    await runPilotAnalysis(prompt1);
    await runPilotAnalysis(prompt2);

    expect(mocks.generateContent).toHaveBeenCalledTimes(2);
  });
});
