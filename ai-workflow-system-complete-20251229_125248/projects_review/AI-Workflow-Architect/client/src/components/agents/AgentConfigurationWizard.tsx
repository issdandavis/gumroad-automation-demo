import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ChevronLeft, 
  ChevronRight, 
  Bot, 
  Brain, 
  Settings, 
  Zap, 
  Shield,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Code,
  Database,
  Globe
} from "lucide-react";

interface AgentConfig {
  name: string;
  description: string;
  model: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  capabilities: string[];
  securityLevel: "low" | "medium" | "high";
  rateLimitPerMinute: number;
  enableFallback: boolean;
  enableLogging: boolean;
  customInstructions: string;
}

const WIZARD_STEPS = [
  { id: "basic", title: "Basic Info", icon: <Bot className="w-5 h-5" /> },
  { id: "model", title: "AI Model", icon: <Brain className="w-5 h-5" /> },
  { id: "capabilities", title: "Capabilities", icon: <Zap className="w-5 h-5" /> },
  { id: "security", title: "Security", icon: <Shield className="w-5 h-5" /> },
  { id: "advanced", title: "Advanced", icon: <Settings className="w-5 h-5" /> },
  { id: "review", title: "Review", icon: <CheckCircle className="w-5 h-5" /> }
];

const AI_MODELS = [
  { id: "claude-3.5-sonnet", name: "Claude 3.5 Sonnet", provider: "Anthropic", description: "Best for complex reasoning and code" },
  { id: "gpt-4o", name: "GPT-4o", provider: "OpenAI", description: "Excellent for general tasks and creativity" },
  { id: "grok-beta", name: "Grok Beta", provider: "xAI", description: "Real-time information and analysis" },
  { id: "gemini-pro", name: "Gemini Pro", provider: "Google", description: "Multimodal capabilities and speed" }
];

const CAPABILITIES = [
  { id: "code", name: "Code Generation", icon: <Code className="w-4 h-4" />, description: "Write and debug code" },
  { id: "data", name: "Data Analysis", icon: <Database className="w-4 h-4" />, description: "Process and analyze data" },
  { id: "web", name: "Web Research", icon: <Globe className="w-4 h-4" />, description: "Search and gather information" },
  { id: "chat", name: "Conversational", icon: <Bot className="w-4 h-4" />, description: "Natural language interaction" },
  { id: "creative", name: "Creative Writing", icon: <Sparkles className="w-4 h-4" />, description: "Generate creative content" }
];

export function AgentConfigurationWizard({ onComplete, onCancel }: { 
  onComplete: (config: AgentConfig) => void;
  onCancel: () => void;
}) {
  const [currentStep, setCurrentStep] = useState(0);
  const [config, setConfig] = useState<AgentConfig>({
    name: "",
    description: "",
    model: "claude-3.5-sonnet",
    temperature: 0.7,
    maxTokens: 4000,
    systemPrompt: "",
    capabilities: [],
    securityLevel: "medium",
    rateLimitPerMinute: 60,
    enableFallback: true,
    enableLogging: true,
    customInstructions: ""
  });

  const updateConfig = (updates: Partial<AgentConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  const toggleCapability = (capabilityId: string) => {
    const capabilities = config.capabilities.includes(capabilityId)
      ? config.capabilities.filter(id => id !== capabilityId)
      : [...config.capabilities, capabilityId];
    updateConfig({ capabilities });
  };

  const nextStep = () => {
    if (currentStep < WIZARD_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 0: // Basic Info
        return config.name.trim() !== "" && config.description.trim() !== "";
      case 1: // Model
        return config.model !== "";
      case 2: // Capabilities
        return config.capabilities.length > 0;
      case 3: // Security
        return true; // Always valid
      case 4: // Advanced
        return true; // Always valid
      case 5: // Review
        return true; // Always valid
      default:
        return false;
    }
  };

  const renderBasicInfo = () => (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Agent Name</Label>
        <Input
          id="name"
          placeholder="e.g., Code Assistant, Research Bot"
          value={config.name}
          onChange={(e) => updateConfig({ name: e.target.value })}
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          placeholder="Describe what this agent will do..."
          value={config.description}
          onChange={(e) => updateConfig({ description: e.target.value })}
          rows={3}
        />
      </div>

      <div className="p-4 rounded-lg bg-muted/50 border border-muted">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5" />
          <div>
            <p className="font-medium text-sm">Naming Tips</p>
            <p className="text-sm text-muted-foreground">
              Choose a clear, descriptive name that reflects the agent's primary function.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderModelSelection = () => (
    <div className="space-y-6">
      <div className="grid gap-4">
        {AI_MODELS.map((model) => (
          <motion.div
            key={model.id}
            className={`