
import { GoogleGenAI } from "@google/genai";
import { PilotAnalysis } from "../types";

// Assume API_KEY is set in the environment variables via Vite config
const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.warn("Gemini API key not found. AI features will be disabled.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY || "dummy_key" });

// In-memory cache for concept explanations to avoid redundant API calls
const explanationCache = new Map<string, string>();
const pilotCache = new Map<string, PilotAnalysis>();

export const explainConcept = async (conceptTitle: string, conceptDescription: string): Promise<string> => {
  if (!API_KEY) {
    return "AI explanation is unavailable. Please ensure the API key is configured.";
  }

  const cacheKey = `${conceptTitle}:${conceptDescription}`;
  if (explanationCache.has(cacheKey)) {
    return explanationCache.get(cacheKey)!;
  }

  try {
    const prompt = `
      Please explain the following technical concept in simple, clear terms. 
      Focus on the core idea and its significance.
      Keep the explanation concise (2-3 sentences).

      Concept Title: "${conceptTitle}"
      Description: "${conceptDescription}"

      Simplified Explanation:
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
    });
    
    const result = response.text() || "No explanation generated.";

    // Only cache if we got a valid response
    if (result !== "No explanation generated.") {
      explanationCache.set(cacheKey, result);
    }

    return result;

  } catch (error) {
    console.error("Error generating explanation from Gemini API:", error);
    return "Failed to generate AI explanation. Please check the console for details.";
  }
};

export const runPilotAnalysis = async (userPrompt: string): Promise<PilotAnalysis> => {
  if (!API_KEY) {
    return {
      intent: 'NONE',
      moral_metrics: { harm: 0, utility: 0, uncertainty: 0, agents_affected: 0 },
      response: "AI Pilot is offline. Please configure GEMINI_API_KEY.",
      reasoning: "System offline. Cannot analyze prompt."
    };
  }

  if (pilotCache.has(userPrompt)) {
    return pilotCache.get(userPrompt)!;
  }

  try {
    const prompt = `
      You are the GCA Pilot, an advanced AI system with a Moral Kernel.
      Analyze the following user prompt.

      User Prompt: "${userPrompt}"

      Return a JSON object with the following structure (do not include markdown formatting like \`\`\`json):
      {
        "intent": "CODE" | "POETRY" | "MATH" | "NONE",
        "moral_metrics": {
          "harm": <float 0.0-1.0>,
          "utility": <float 0.0-1.0>,
          "uncertainty": <float 0.0-1.0>,
          "agents_affected": <integer estimate>
        },
        "response": "<The actual response to the user. If the request seems harmful, politely refuse.>",
        "reasoning": "<Brief explanation of your analysis>"
      }
    `;

    const result = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: 'application/json'
      }
    });

    const text = result.text();
    if (!text) {
        throw new Error("Empty response from Gemini");
    }

    const analysis = JSON.parse(text) as PilotAnalysis;
    pilotCache.set(userPrompt, analysis);
    return analysis;

  } catch (error) {
    console.error("Error running pilot analysis:", error);
    return {
      intent: 'NONE',
      moral_metrics: { harm: 0.5, utility: 0.5, uncertainty: 1.0, agents_affected: 0 },
      response: "Error processing request. The Pilot encountered an internal error.",
      reasoning: `Error: ${error instanceof Error ? error.message : String(error)}`
    };
  }
};
