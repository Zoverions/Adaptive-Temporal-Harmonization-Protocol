
import { GoogleGenAI } from "@google/genai";

// Assume API_KEY is set in the environment variables
const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.warn("Gemini API key not found. AI features will be disabled.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY });

// In-memory cache to store AI explanations and avoid redundant API calls
const explanationCache = new Map<string, string>();

export const explainConcept = async (conceptTitle: string, conceptDescription: string): Promise<string> => {
  if (!API_KEY) {
    return "AI explanation is unavailable. Please ensure the API key is configured.";
  }

  // Generate a cache key based on the concept title and description
  const cacheKey = `${conceptTitle}:${conceptDescription}`;

  // Check if we already have a cached explanation for this concept
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
    
    const explanation = response.text;

    // Store the result in cache before returning
    explanationCache.set(cacheKey, explanation);

    return explanation;

  } catch (error) {
    console.error("Error generating explanation from Gemini API:", error);
    return "Failed to generate AI explanation. Please check the console for details.";
  }
};
