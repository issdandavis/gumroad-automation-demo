
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

import Layout from "@/components/dashboard/Layout";
import { EnhancedAgentCard } from "@/components/dashboard/EnhancedAgentCard";
import { EnhancedActivityFeed } from "@/components/dashboard/EnhancedActivityFeed";
import { ModernCommandInput } from "@/components/dashboard/ModernCommandInput";
import { SystemMetrics } from "@/components/dashboard/SystemMetrics";
import IntegrationStatus from "@/components/dashboard/IntegrationStatus";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Sparkles, 
  Zap, 
  Brain, 
  Settings, 
  BarChart3,
  Users,
  Workflow,
  Plus
} from "lucide-react";

export default function EnhancedDashboard() {
  const agents = [
    { 
      name: "Claude 3.5", 
      role: "Code Architect", 
      status: "executing" as const, 
      icon: "claude" as const, 
      tasksCompleted: 142,
      currentTask: "Refactoring authentication system",
      efficiency: 98,
      uptime: "99.9%"
    },
    { 
      name: "ChatGPT-4o", 
      role: "Documentation Lead", 
      status: "thinking" as const, 
      icon: "gpt" as const, 
      tasksCompleted: 89,
      currentTask: "Generating API documentation",
      efficiency: 94,
      uptime: "99.7%"
    },
    { 
      name: "Grok Beta", 
      role: "Research Analyst", 
      status: "idle" as const, 
      icon: "grok" as const, 
      tasksCompleted: 56,
      efficiency: 92,
      uptime: "99.5%"
    },
  ];

  const handleAgentAction = (agentName: string, action: "start" | "pause" | "configure") => {
    console.log(`Agent ${agentName}: ${action}`);
    // Handle agent actions
  };

  return (
    <Layout>
      <div className="space-y-8">
        
        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6"
        >
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight text-glow">
              AI Command Center
            </h1>
            <p className="text-muted-foreground text-lg">
              Orchestrating intelligent automation across your entire stack
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge className="px-4 py-2 bg-primary/10 border border-primary/20 text-primary flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="font-mono text-sm">SYSTEM OPTIMAL</span>
            </Badge>
            
            <Button variant="outline" className="gap-2">
              <Settings className="w-4 h-4" />
              Configure
            </Button>
            
            <Button className="gap-2 bg-primary hover:bg-primary/90">
              <Plus className="w-4 h-4" />
              Add Agent
            </Button>
          </div>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4"
        >
          <Card className="glass-card border-2 border-primary/20">
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <Brain className="w-5 h-5 text-primary" />
              </div>
              <div className="text-2xl font-bold text-glow">3</div>
              <div className="text-xs text-muted-foreground">Active Agents</div>
            </CardContent>
          </Card>
          
          <Card className="glass-card border-2 border-green-500/20">
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <Workflow className="w-5 h-5 text-green-400" />
              </div>
              <div className="text-2xl font-bold text-glow">287</div>
              <div className="text-xs text-muted-foreground">Tasks Completed</div>
            </CardContent>
          </Card>
          
          <Card className="glass-card border-2 border-blue-500/20">
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <BarChart3 className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-2xl font-bold text-glow">95%</div>
              <div className="text-xs text-muted-foreground">Efficiency</div>
            </CardContent>
          </Card>
          
          <Card className="glass-card border-2 border-purple-500/20">
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <Users className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-2xl font-bold text-glow">12</div>
              <div className="text-xs text-muted-foreground">Integrations</div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Status Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <IntegrationStatus />
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          
          {/* Left Column: Agents & Workflows */}
          <div className="xl:col-span-2 space-y-8">
            
            {/* Agent Cards */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold flex items-center gap-3">
                  <Sparkles className="w-6 h-6 text-primary" />
                  AI Agents
                </h2>
                <Button variant="ghost" size="sm" className="gap-2">
                  <Settings className="w-4 h-4" />
                  Manage All
                </Button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {agents.map((agent, i) => (
                  <motion.div
                    key={agent.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + i * 0.1 }}
                  >
                    <EnhancedAgentCard 
                      {...agent} 
                      onAction={(action) => handleAgentAction(agent.name, action)}
                    />
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* System Metrics */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <SystemMetrics />
            </motion.div>

            {/* Workflow Visualization */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle className="text-xl font-bold flex items-center gap-2">
                    <Zap className="w-5 h-5 text-primary" />
                    Active Workflows
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative h-64 border border-white/10 rounded-xl bg-black/20 overflow-hidden flex items-center justify-center">
                    <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px]" />
                    
                    <div className="flex items-center gap-8 relative z-10">
                      <motion.div 
                        className="p-6 rounded-xl bg-card border border-primary/50 shadow-[0_0_20px_rgba(0,255,255,0.3)] flex flex-col items-center gap-3"
                        animate={{ 
                          boxShadow: [
                            "0_0_20px_rgba(0,255,255,0.3)",
                            "0_0_30px_rgba(0,255,255,0.5)", 
                            "0_0_20px_rgba(0,255,255,0.3)"
                          ]
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <div className="w-10 h-10 rounded-full bg-white text-black flex items-center justify-center font-bold text-lg">G</div>
                        <span className="text-sm font-mono">GitHub</span>
                      </motion.div>
                      
                      <motion.div 
                        className="h-[3px] w-20 bg-gradient-to-r from-primary/50 to-purple-500/50 relative"
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      >
                        <motion.div 
                          className="absolute top-1/2 w-3 h-3 bg-white rounded-full shadow-[0_0_15px_white]"
                          animate={{ left: ["-6px", "calc(100% - 6px)"] }}
                          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        />
                      </motion.div>
                      
                      <motion.div 
                        className="p-6 rounded-xl bg-card border border-purple-500/50 shadow-[0_0_20px_rgba(168,85,247,0.3)] flex flex-col items-center gap-3"
                        animate={{ 
                          boxShadow: [
                            "0_0_20px_rgba(168,85,247,0.3)",
                            "0_0_30px_rgba(168,85,247,0.5)",
                            "0_0_20px_rgba(168,85,247,0.3)"
                          ]
                        }}
                        transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                      >
                        <div className="w-10 h-10 rounded-full bg-purple-500 text-white flex items-center justify-center font-bold text-lg">A</div>
                        <span className="text-sm font-mono">AI Agent</span>
                      </motion.div>
                      
                      <motion.div 
                        className="h-[3px] w-20 bg-gradient-to-r from-purple-500/50 to-blue-500/50 relative"
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 1 }}
                      >
                        <motion.div 
                          className="absolute top-1/2 w-3 h-3 bg-white rounded-full shadow-[0_0_15px_white]"
                          animate={{ left: ["-6px", "calc(100% - 6px)"] }}
                          transition={{ duration: 2, repeat: Infinity, ease: "linear", delay: 1 }}
                        />
                      </motion.div>
                      
                      <motion.div 
                        className="p-6 rounded-xl bg-card border border-blue-500/50 shadow-[0_0_20px_rgba(59,130,246,0.3)] flex flex-col items-center gap-3"
                        animate={{ 
                          boxShadow: [
                            "0_0_20px_rgba(59,130,246,0.3)",
                            "0_0_30px_rgba(59,130,246,0.5)",
                            "0_0_20px_rgba(59,130,246,0.3)"
                          ]
                        }}
                        transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                      >
                        <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold text-lg">D</div>
                        <span className="text-sm font-mono">Deploy</span>
                      </motion.div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Right Column: Activity & Command */}
          <div className="space-y-8 flex flex-col">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              className="flex-1"
            >
              <EnhancedActivityFeed />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <ModernCommandInput />
            </motion.div>
          </div>
        </div>
      </div>
    </Layout>
  );
}