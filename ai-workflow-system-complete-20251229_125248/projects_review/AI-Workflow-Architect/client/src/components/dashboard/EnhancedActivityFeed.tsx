
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

import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  Zap, 
  Code, 
  Database, 
  Globe, 
  MessageSquare,
  ArrowRight,
  MoreHorizontal,
  Filter
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ActivityItem {
  id: string;
  type: "success" | "pending" | "error" | "info";
  title: string;
  description: string;
  timestamp: string;
  agent: string;
  category: "code" | "data" | "web" | "chat" | "system";
  duration?: string;
  metadata?: {
    linesChanged?: number;
    filesModified?: number;
    apiCalls?: number;
  };
}

const mockActivities: ActivityItem[] = [
  {
    id: "1",
    type: "success",
    title: "API Integration Complete",
    description: "Successfully connected Stripe payment gateway",
    timestamp: "2 min ago",
    agent: "Claude 3.5",
    category: "code",
    duration: "45s",
    metadata: { linesChanged: 127, filesModified: 3 }
  },
  {
    id: "2", 
    type: "pending",
    title: "Database Migration",
    description: "Migrating user data to new schema",
    timestamp: "5 min ago",
    agent: "GPT-4o",
    category: "data",
    metadata: { apiCalls: 1247 }
  },
  {
    id: "3",
    type: "success", 
    title: "Documentation Generated",
    description: "Created API docs for payment endpoints",
    timestamp: "12 min ago",
    agent: "Grok Beta",
    category: "code",
    duration: "2m 15s",
    metadata: { filesModified: 8 }
  },
  {
    id: "4",
    type: "error",
    title: "Deployment Failed",
    description: "Build failed due to missing environment variables",
    timestamp: "18 min ago", 
    agent: "Claude 3.5",
    category: "system"
  },
  {
    id: "5",
    type: "info",
    title: "Market Research Complete",
    description: "Analyzed 50 competitor pricing strategies",
    timestamp: "25 min ago",
    agent: "Perplexity",
    category: "web",
    duration: "8m 32s"
  }
];

const typeConfig = {
  success: {
    icon: CheckCircle,
    color: "text-green-400",
    bgColor: "bg-green-500/10",
    borderColor: "border-green-500/30"
  },
  pending: {
    icon: Clock,
    color: "text-blue-400", 
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/30"
  },
  error: {
    icon: AlertTriangle,
    color: "text-red-400",
    bgColor: "bg-red-500/10", 
    borderColor: "border-red-500/30"
  },
  info: {
    icon: Zap,
    color: "text-purple-400",
    bgColor: "bg-purple-500/10",
    borderColor: "border-purple-500/30"
  }
};

const categoryIcons = {
  code: Code,
  data: Database,
  web: Globe,
  chat: MessageSquare,
  system: Zap
};

export function EnhancedActivityFeed() {
  return (
    <Card className="glass-panel h-full flex flex-col">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <span className="w-1 h-6 bg-primary rounded-full" />
            Activity Feed
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
              <Filter className="w-3 h-3" />
            </Button>
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
              <MoreHorizontal className="w-3 h-3" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 p-0">
        <ScrollArea className="h-full px-6 pb-6">
          <div className="space-y-4">
            <AnimatePresence>
              {mockActivities.map((activity, index) => {
                const config = typeConfig[activity.type];
                const Icon = config.icon;
                const CategoryIcon = categoryIcons[activity.category];

                return (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.1 }}
                    className={cn(
                      "relative p-4 rounded-xl border transition-all duration-300 hover:scale-[1.02]",
                      config.bgColor,
                      config.borderColor,
                      "backdrop-blur-sm cursor-pointer group"
                    )}
                  >
                    {/* Status Indicator */}
                    <div className="flex items-start gap-3">
                      <div className={cn(
                        "flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center",
                        config.bgColor,
                        "border",
                        config.borderColor
                      )}>
                        <Icon className={cn("w-4 h-4", config.color)} />
                      </div>

                      <div className="flex-1 min-w-0">
                        {/* Header */}
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div className="flex items-center gap-2 min-w-0">
                            <h4 className="font-semibold text-sm truncate">
                              {activity.title}
                            </h4>
                            <CategoryIcon className="w-3 h-3 text-muted-foreground flex-shrink-0" />
                          </div>
                          <ArrowRight className="w-3 h-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                        </div>

                        {/* Description */}
                        <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
                          {activity.description}
                        </p>

                        {/* Metadata */}
                        {activity.metadata && (
                          <div className="flex flex-wrap gap-2 mb-3">
                            {activity.metadata.linesChanged && (
                              <Badge variant="secondary" className="text-xs px-2 py-0.5">
                                +{activity.metadata.linesChanged} lines
                              </Badge>
                            )}
                            {activity.metadata.filesModified && (
                              <Badge variant="secondary" className="text-xs px-2 py-0.5">
                                {activity.metadata.filesModified} files
                              </Badge>
                            )}
                            {activity.metadata.apiCalls && (
                              <Badge variant="secondary" className="text-xs px-2 py-0.5">
                                {activity.metadata.apiCalls} calls
                              </Badge>
                            )}
                          </div>
                        )}

                        {/* Footer */}
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{activity.agent}</span>
                            {activity.duration && (
                              <>
                                <span>•</span>
                                <span>{activity.duration}</span>
                              </>
                            )}
                          </div>
                          <span>{activity.timestamp}</span>
                        </div>
                      </div>
                    </div>

                    {/* Pending Animation */}
                    {activity.type === "pending" && (
                      <div className="absolute inset-0 rounded-xl overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-blue-400 to-transparent animate-pulse" />
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}