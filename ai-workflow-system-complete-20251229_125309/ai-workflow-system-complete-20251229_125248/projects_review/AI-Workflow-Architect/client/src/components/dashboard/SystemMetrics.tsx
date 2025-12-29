
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Cpu, 
  HardDrive, 
  Zap, 
  DollarSign, 
  Clock, 
  TrendingUp,
  Activity,
  Server
} from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  change?: number;
  changeLabel?: string;
  icon: React.ComponentType<{ className?: string }>;
  color: "primary" | "green" | "blue" | "purple" | "orange";
  progress?: number;
  status?: "optimal" | "warning" | "critical";
}

const colorConfig = {
  primary: {
    text: "text-primary",
    bg: "bg-primary/10",
    border: "border-primary/30",
    progress: "bg-primary"
  },
  green: {
    text: "text-green-400", 
    bg: "bg-green-500/10",
    border: "border-green-500/30",
    progress: "bg-green-500"
  },
  blue: {
    text: "text-blue-400",
    bg: "bg-blue-500/10", 
    border: "border-blue-500/30",
    progress: "bg-blue-500"
  },
  purple: {
    text: "text-purple-400",
    bg: "bg-purple-500/10",
    border: "border-purple-500/30", 
    progress: "bg-purple-500"
  },
  orange: {
    text: "text-orange-400",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    progress: "bg-orange-500"
  }
};

function MetricCard({ 
  title, 
  value, 
  unit, 
  change, 
  changeLabel, 
  icon: Icon, 
  color, 
  progress,
  status = "optimal"
}: MetricCardProps) {
  const config = colorConfig[color];
  const isPositive = change && change > 0;

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card className={cn(
        "glass-card hover:glass-panel transition-all duration-300 border-2",
        config.border
      )}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className={cn(
              "w-10 h-10 rounded-lg flex items-center justify-center",
              config.bg,
              "border",
              config.border
            )}>
              <Icon className={cn("w-5 h-5", config.text)} />
            </div>
            
            {status !== "optimal" && (
              <Badge 
                variant={status === "warning" ? "secondary" : "destructive"}
                className="text-xs"
              >
                {status}
              </Badge>
            )}
          </div>

          <div className="space-y-2">
            <p className="text-xs text-muted-foreground font-medium">{title}</p>
            
            <div className="flex items-baseline gap-1">
              <span className={cn("text-2xl font-bold", config.text, "text-glow")}>
                {value}
              </span>
              {unit && (
                <span className="text-sm text-muted-foreground">{unit}</span>
              )}
            </div>

            {progress !== undefined && (
              <div className="space-y-1">
                <Progress 
                  value={progress} 
                  className="h-2"
                  // Custom progress bar color would need to be handled via CSS variables
                />
                <p className="text-xs text-muted-foreground">{progress}% capacity</p>
              </div>
            )}

            {change !== undefined && changeLabel && (
              <div className="flex items-center gap-1 text-xs">
                <TrendingUp className={cn(
                  "w-3 h-3",
                  isPositive ? "text-green-400" : "text-red-400"
                )} />
                <span className={isPositive ? "text-green-400" : "text-red-400"}>
                  {isPositive ? "+" : ""}{change}%
                </span>
                <span className="text-muted-foreground">{changeLabel}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function SystemMetrics() {
  const metrics = [
    {
      title: "CPU Usage",
      value: 23,
      unit: "%",
      change: -5,
      changeLabel: "vs last hour",
      icon: Cpu,
      color: "blue" as const,
      progress: 23,
      status: "optimal" as const
    },
    {
      title: "Memory",
      value: 8.2,
      unit: "GB",
      change: 12,
      changeLabel: "vs last hour", 
      icon: HardDrive,
      color: "green" as const,
      progress: 68,
      status: "optimal" as const
    },
    {
      title: "API Calls",
      value: "2.4K",
      change: 23,
      changeLabel: "today",
      icon: Zap,
      color: "primary" as const,
      status: "optimal" as const
    },
    {
      title: "Cost Today",
      value: "$12.45",
      change: -8,
      changeLabel: "vs yesterday",
      icon: DollarSign,
      color: "green" as const,
      status: "optimal" as const
    },
    {
      title: "Avg Response",
      value: 1.2,
      unit: "s",
      change: -15,
      changeLabel: "improvement",
      icon: Clock,
      color: "purple" as const,
      status: "optimal" as const
    },
    {
      title: "Uptime",
      value: "99.9",
      unit: "%",
      change: 0.1,
      changeLabel: "this month",
      icon: Server,
      color: "orange" as const,
      status: "optimal" as const
    }
  ];

  return (
    <Card className="glass-panel">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-bold flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary" />
          System Metrics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <MetricCard {...metric} />
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}