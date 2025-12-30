import { GoogleGenAI, Type, Schema } from "@google/genai";
import { GeneratedPlanResponse, StepAdvice } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const modelName = "gemini-2.5-flash";

/**
 * Generates a structured project plan based on the user's vague goal.
 */
export const generateProjectPlan = async (userGoal: string): Promise<GeneratedPlanResponse> => {
  const schema: Schema = {
    type: Type.OBJECT,
    properties: {
      projectName: { type: Type.STRING, description: "A catchy, professional title for this workflow." },
      projectDescription: { type: Type.STRING, description: "A brief summary of what will be achieved." },
      steps: {
        type: Type.ARRAY,
        items: {
          type: Type.OBJECT,
          properties: {
            title: { type: Type.STRING, description: "Actionable title for the step." },
            description: { type: Type.STRING, description: "One sentence summary of the step." },
            estimatedTime: { type: Type.STRING, description: "E.g., '5 mins', '1 hour'." },
            category: { type: Type.STRING, description: "One of: setup, design, marketing, products, settings" },
          },
          required: ["title", "description", "estimatedTime", "category"],
        },
      },
    },
    required: ["projectName", "projectDescription", "steps"],
  };

  const response = await ai.models.generateContent({
    model: modelName,
    contents: `The user is a Shopify beginner. Their goal is: "${userGoal}". 
    Break this down into a strict, logical, step-by-step checklist to achieve this goal within Shopify's admin. 
    Focus on specific actions (e.g., 'Go to Products > Add Product').`,
    config: {
      responseMimeType: "application/json",
      responseSchema: schema,
      systemInstruction: "You are an expert Shopify Setup Assistant. You break complex tasks into bite-sized, non-overwhelming steps for beginners.",
    },
  });

  const text = response.text;
  if (!text) throw new Error("No response from AI");
  
  return JSON.parse(text) as GeneratedPlanResponse;
};

/**
 * Gets detailed advice and "how-to" for a specific step.
 */
export const getStepDetails = async (stepTitle: string, context: string): Promise<StepAdvice> => {
  const schema: Schema = {
    type: Type.OBJECT,
    properties: {
      detailedInstructions: { type: Type.STRING, description: "Step-by-step markdown instructions with bold menu items." },
      whyItMatters: { type: Type.STRING, description: "Explanation of business value." },
      commonPitfalls: { 
        type: Type.ARRAY, 
        items: { type: Type.STRING },
        description: "List of 2-3 mistakes beginners make here."
      },
    },
    required: ["detailedInstructions", "whyItMatters", "commonPitfalls"],
  };

  const response = await ai.models.generateContent({
    model: modelName,
    contents: `Explain exactly how to perform this Shopify task: "${stepTitle}". Context: ${context}.`,
    config: {
      responseMimeType: "application/json",
      responseSchema: schema,
      systemInstruction: "You are a patient, clear Shopify tutor. Use bold text for UI elements (e.g., **Settings** > **Shipping**). Keep it practical.",
    },
  });

   const text = response.text;
   if (!text) throw new Error("No response from AI");

   // We assign a temp ID in the component, the AI just returns the content
   const data = JSON.parse(text);
   return {
     stepId: "", 
     ...data
   } as StepAdvice;
};