
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

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Send, 
  Mic, 
  Paperclip, 
  Sparkles, 
  Zap,
  Brain,
  Code,
  Database,
  Globe,
  MessageSquare
} from "lucide-react";
import { cn } from "@/lib/utils";

interface CommandSuggestion {
  text: string;
  category: "code" | "data" | "web" | "chat" | "ai";
  icon: React.ComponentType<{ className?: string }>;
}

const suggestions: CommandSuggestion[] = [
  { text: "Deploy to production", category: "code", icon: Code },
  { text: "Analyze user metrics", category: "data", icon: Database },
  { text: "Research competitors", category: "web", icon: Globe },
  { text: "Generate documentation", category: "ai", icon: Brain },
  { text: "Schedule team meeting", category: "chat", icon: MessageSquare },
];

const categoryColors = {
  code: "bg-blue-500/10 text-blue-400 border-blue-500/30",
  data: "bg-green-500/10 text-green-400 border-green-500/30", 
  web: "bg-purple-500/10 text-purple-400 border-purple-500/30",
  ai: "bg-primary/10 text-primary border-primary/30",
  chat: "bg-orange-500/10 text-orange-400 border-orange-500/30"
};

export function ModernCommandInput() {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    
    setIsProcessing(true);
    // Simulate processing
    setTimeout(() => {
      setInput("");
      setIsProcessing(false);
      setShowSuggestions(false);
    }, 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const insertSuggestion = (suggestion: CommandSuggestion) => {
    setInput(suggestion.text);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  useEffect(() => {
    if (input.length > 0) {
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  }, [input]);

  return (
    <div className="space-y-4">
      {/* Suggestions */}
      <AnimatePresence>
        {showSuggestions && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="space-y-2"
          >
            <p className="text-xs text-muted-foreground px-2">Quick Actions</p>
            <div className="flex flex-wrap gap-2">
              {suggestions
                .filter(s => s.text.toLowerCase().includes(input.toLowerCase()))
                .slice(0, 3)
                .map((suggestion, i) => {
                  const Icon = suggestion.icon;
                  return (
                    <motion.button
                      key={suggestion.text}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.1 }}
                      onClick={() => insertSuggestion(suggestion)}
                      className={cn(
                        "flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all hover:scale-105",
                        categoryColors[suggestion.category],
                        "border backdrop-blur-sm"
                      )}
                    >
                      <Icon className="w-3 h-3" />
                      {suggestion.text}
                    </motion.button>
                  );
                })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Input */}
      <Card className="glass-panel border-2 border-primary/20 hover:border-primary/40 transition-all duration-300">
        <CardContent className="p-4">
          <div className="flex items-end gap-3">
            {/* Input Area */}
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Command your AI agents..."
                className="w-full bg-transparent border-none outline-none resize-none text-sm placeholder:text-muted-foreground min-h-[40px] max-h-[120px] py-2"
                rows={1}
                style={{ 
                  height: 'auto',
                  minHeight: '40px'
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = target.scrollHeight + 'px';
                }}
              />
              
              {/* Processing Indicator */}
              <AnimatePresence>
                {isProcessing && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm rounded-lg"
                  >
                    <div className="flex items-center gap-2 text-primary">
                      <Sparkles className="w-4 h-4 animate-spin" />
                      <span className="text-sm font-medium">Processing...</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => setIsRecording(!isRecording)}
              >
                <Mic className={cn(
                  "w-4 h-4 transition-colors",
                  isRecording && "text-red-400 animate-pulse"
                )} />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
              >
                <Paperclip className="w-4 h-4" />
              </Button>

              <Button
                onClick={handleSubmit}
                disabled={!input.trim() || isProcessing}
                size="sm"
                className="h-8 px-3 bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                {isProcessing ? (
                  <Sparkles className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-1" />
                    Send
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Status Bar */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/5">
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span>3 agents online</span>
              </div>
              <div className="flex items-center gap-1">
                <Zap className="w-3 h-3" />
                <span>Fast mode</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs px-2 py-0.5">
                ⌘ + Enter to send
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}