
/**
 * Infrastructure Update: 2025-12-29T09:27:50.260Z
 * 
 * This file has been updated as part of a comprehensive infrastructure
 * synchronization to ensure all components are versioned consistently.
 * 
 * Changes include:
 * - Enhanced UI components with Figma design integration
 * - Modern dashboard with glassmorphism effects
 * - Improved accessibility and performance optimizations
 * - Updated build configuration and dependencies
 */

import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Brain, 
  Zap, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Play, 
  Pause, 
  Settings,
  TrendingUp,
  Activity
} from "lucide-react";
import { cn } from "@/lib/utils";

interface EnhancedAgentCardProps {
  name: string;
  role: string;
  status: "thinking" | "idle" | "executing" | "error" | "completed";
  icon: "claude" | "gpt" | "grok" | "gemini" | "perplexity";
  tasksCompleted: number;
  currentTask?: string;
  efficiency?: number;
  uptime?: string;
  onAction?: (action: "start" | "pause" | "configure") => void;
}

const statusConfig = {
  thinking: {
    color: "text-blue-400",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/30",
    icon: Brain,
    label: "Analyzing",
    pulse: true
  },
  idle: {
    color: "text-gray-400", 
    bgColor: "bg-gray-500/10",
    borderColor: "border-gray-500/30",
    icon: Clock,
    label: "Standby",
    pulse: false
  },
  executing: {
    color: "text-primary",
    bgColor: "bg-primary/10", 
    borderColor: "border-primary/30",
    icon: Zap,
    label: "Active",
    pulse: true
  },
  error: {
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/30", 
    icon: AlertCircle,
    label: "Error",
    pulse: true
  },
  completed: {
    color: "text-green-400",
    bgColor: "bg-green-500/10",
    borderColor: "border-green-500/30",
    icon: CheckCircle,
    label: "Complete",
    pulse: false
  }
};

const agentIcons = {
  claude: "🤖",
  gpt: "🧠", 
  grok: "⚡",
  gemini: "💎",
  perplexity: "🔍"
};

export function EnhancedAgentCard({
  name,
  role,
  status,
  icon,
  tasksCompleted,
  currentTask,
  efficiency = 95,
  uptime = "99.9%",
  onAction
}: EnhancedAgentCardProps) {
  const config = statusConfig[status];
  const StatusIcon = config.icon;

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      transition={{ duration: 0.2 }}
    >
      <Card className={cn(
        "glass-card hover:glass-panel transition-all duration-300 relative overflow-hidden",
        config.borderColor,
        "border-2"
      )}>
        {/* Status Indicator Bar */}
        <div className={cn(
          "absolute top-0 left-0 right-0 h-1",
          config.bgColor,
          config.pulse && "animate-pulse"
        )} />

        <CardContent className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center text-2xl",
                  config.bgColor,
                  "border",
                  config.borderColor
                )}>
                  {agentIcons[icon]}
                </div>
                {config.pulse && (
                  <div className={cn(
                    "absolute -top-1 -right-1 w-4 h-4 rounded-full",
                    config.bgColor,
                    "animate-ping"
                  )} />
                )}
              </div>
              <div>
                <h3 className="font-bold text-lg text-glow">{name}</h3>
                <p className="text-sm text-muted-foreground">{role}</p>
              </div>
            </div>

            <Badge 
              variant="secondary" 
              className={cn(
                "flex items-center gap-1 px-2 py-1",
                config.bgColor,
                config.color,
                "border",
                config.borderColor
              )}
            >
              <StatusIcon className="w-3 h-3" />
              {config.label}
            </Badge>
          </div>

          {/* Current Task */}
          {currentTask && (
            <div className="mb-4 p-3 rounded-lg bg-muted/50 border border-white/5">
              <p className="text-xs text-muted-foreground mb-1">Current Task</p>
              <p className="text-sm font-medium truncate">{currentTask}</p>
            </div>
          )}

          {/* Metrics */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <CheckCircle className="w-3 h-3 text-green-400" />
                <span className="text-xs text-muted-foreground">Tasks</span>
              </div>
              <p className="font-bold text-lg text-glow">{tasksCompleted}</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <TrendingUp className="w-3 h-3 text-blue-400" />
                <span className="text-xs text-muted-foreground">Efficiency</span>
              </div>
              <p className="font-bold text-lg text-glow">{efficiency}%</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Activity className="w-3 h-3 text-purple-400" />
                <span className="text-xs text-muted-foreground">Uptime</span>
              </div>
              <p className="font-bold text-lg text-glow">{uptime}</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="flex-1 h-8"
              onClick={() => onAction?.(status === "executing" ? "pause" : "start")}
            >
              {status === "executing" ? (
                <>
                  <Pause className="w-3 h-3 mr-1" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="w-3 h-3 mr-1" />
                  Start
                </>
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0"
              onClick={() => onAction?.("configure")}
            >
              <Settings className="w-3 h-3" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}