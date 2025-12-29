export interface Step {
  id: string;
  title: string;
  description: string;
  isCompleted: boolean;
  estimatedTime?: string;
  category: 'setup' | 'design' | 'marketing' | 'products' | 'settings';
}

export interface Project {
  id: string;
  name: string;
  description: string;
  createdAt: number;
  steps: Step[];
  progress: number; // 0 to 100
}

export interface StepAdvice {
  stepId: string;
  detailedInstructions: string; // Markdown supported
  whyItMatters: string;
  commonPitfalls: string[];
}

// AI Service Response Types
export interface GeneratedPlanResponse {
  projectName: string;
  projectDescription: string;
  steps: {
    title: string;
    description: string;
    estimatedTime: string;
    category: string;
  }[];
}