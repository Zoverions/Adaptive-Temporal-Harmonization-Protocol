
import { GoogleGenAI } from "@google/genai";

// Assume API_KEY is set in the environment variables
const API_KEY = process.env.API_KEY;

let ai: GoogleGenAI | null = null;

if (!API_KEY) {
  console.warn("Gemini API key not found. AI features will be disabled.");
} else {
  ai = new GoogleGenAI({ apiKey: API_KEY });
}

export const explainConcept = async (conceptTitle: string, conceptDescription: string): Promise<string> => {
  if (!API_KEY || !ai) {
    return "AI explanation is unavailable. Please ensure the API key is configured.";
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
    
    return response.text;

  } catch (error) {
    console.error("Error generating explanation from Gemini API:", error);
    return "Failed to generate AI explanation. Please check the console for details.";
  }
};
