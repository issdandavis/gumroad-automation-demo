
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

import { useState } from "react";
import Layout from "@/components/dashboard/Layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { MessageCircle, Users, Play, Send, Plus, Loader2, ArrowLeft } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useToast } from "@/hooks/use-toast";

interface Provider {
  id: string;
  name: string;
  role: string;
  signOff: string;
}

interface RoundtableMessage {
  id: string;
  sessionId: string;
  senderType: "user" | "ai" | "system";
  senderId: string | null;
  provider: string | null;
  model: string | null;
  content: string;
  signature: string | null;
  sequenceNumber: number;
  tokensUsed: number | null;
  responseTimeMs: number | null;
  createdAt: string;
}

interface RoundtableSession {
  id: string;
  title: string;
  topic: string | null;
  activeProviders: string[];
  orchestrationMode: string;
  status: string;
  currentTurn: number;
  maxTurns: number;
  createdAt: string;
  messages?: RoundtableMessage[];
}

const PROVIDER_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  openai: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/30" },
  anthropic: { bg: "bg-orange-500/10", text: "text-orange-400", border: "border-orange-500/30" },
  xai: { bg: "bg-purple-500/10", text: "text-purple-400", border: "border-purple-500/30" },
  perplexity: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/30" },
  google: { bg: "bg-cyan-500/10", text: "text-cyan-400", border: "border-cyan-500/30" },
};

function NewSessionDialog({ providers, onCreated }: { providers: Provider[]; onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [topic, setTopic] = useState("");
  const [selectedProviders, setSelectedProviders] = useState<string[]>([]);
  const { toast } = useToast();

  const createSession = useMutation({
    mutationFn: async () => {
      const res = await apiRequest("POST", "/api/roundtable/sessions", {
        title,
        topic: topic || undefined,
        activeProviders: selectedProviders,
      });
      return res.json();
    },
    onSuccess: () => {
      toast({ title: "Session created", description: "Your roundtable session is ready." });
      setOpen(false);
      setTitle("");
      setTopic("");
      setSelectedProviders([]);
      onCreated();
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const toggleProvider = (id: string) => {
    setSelectedProviders((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="gap-2" data-testid="button-new-session">
          <Plus className="w-4 h-4" /> New Roundtable
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Start AI Roundtable</DialogTitle>
          <DialogDescription>
            Create a new discussion where multiple AIs can collaborate and debate.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="title">Session Title</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Architecture Review"
              data-testid="input-session-title"
            />
          </div>
          <div>
            <Label htmlFor="topic">Discussion Topic</Label>
            <Textarea
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="What should the AIs discuss?"
              rows={3}
              data-testid="input-session-topic"
            />
          </div>
          <div>
            <Label>Select AI Participants</Label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {providers.map((provider) => {
                const colors = PROVIDER_COLORS[provider.id] || { bg: "bg-gray-500/10", text: "text-gray-400", border: "border-gray-500/30" };
                const isSelected = selectedProviders.includes(provider.id);
                return (
                  <label
                    key={provider.id}
                    className={`flex items-center space-x-2 p-2 rounded-lg border ${
                      isSelected ? colors.border : "border-white/10"
                    } ${isSelected ? colors.bg : "bg-white/5"} cursor-pointer transition-colors`}
                  >
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={() => toggleProvider(provider.id)}
                      data-testid={`checkbox-provider-${provider.id}`}
                    />
                    <div>
                      <span className={`font-medium ${isSelected ? colors.text : ""}`}>
                        {provider.name}
                      </span>
                      <p className="text-xs text-muted-foreground">{provider.role}</p>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
          <Button
            onClick={() => createSession.mutate()}
            disabled={!title || selectedProviders.length === 0 || createSession.isPending}
            className="w-full"
            data-testid="button-create-session"
          >
            {createSession.isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Create Session
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function SessionView({ sessionId, onBack }: { sessionId: string; onBack: () => void }) {
  const [userMessage, setUserMessage] = useState("");
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: session, isLoading } = useQuery<RoundtableSession>({
    queryKey: ["/api/roundtable/sessions", sessionId],
    queryFn: async () => {
      const res = await fetch(`/api/roundtable/sessions/${sessionId}`, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch session");
      return res.json();
    },
    refetchInterval: 5000,
  });

  const sendMessage = useMutation({
    mutationFn: async () => {
      const res = await apiRequest("POST", `/api/roundtable/sessions/${sessionId}/message`, { content: userMessage });
      return res.json();
    },
    onSuccess: () => {
      setUserMessage("");
      queryClient.invalidateQueries({ queryKey: ["/api/roundtable/sessions", sessionId] });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const runRound = useMutation({
    mutationFn: async () => {
      const res = await apiRequest("POST", `/api/roundtable/sessions/${sessionId}/round`);
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/roundtable/sessions", sessionId] });
      toast({ title: "Round complete", description: "All AIs have responded." });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  if (isLoading || !session) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const messages = session.messages || [];

  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      <div className="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="icon" onClick={onBack} data-testid="button-back">
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="flex-1">
          <h2 className="text-xl font-bold" data-testid="text-session-title">{session.title}</h2>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Badge variant={session.status === "active" ? "default" : "secondary"} data-testid="badge-session-status">
              {session.status}
            </Badge>
            <span>Turn {session.currentTurn} / {session.maxTurns}</span>
            <span>•</span>
            <span>{session.activeProviders?.length || 0} AIs</span>
          </div>
        </div>
        <Button
          onClick={() => runRound.mutate()}
          disabled={runRound.isPending || session.status !== "active"}
          className="gap-2"
          data-testid="button-run-round"
        >
          {runRound.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          Run AI Round
        </Button>
      </div>

      {session.topic && (
        <div className="bg-white/5 rounded-lg p-3 mb-4 border border-white/10">
          <p className="text-sm text-muted-foreground">
            <strong>Topic:</strong> {session.topic}
          </p>
        </div>
      )}

      <ScrollArea className="flex-1 pr-4">
        <div className="space-y-4">
          <AnimatePresence>
            {messages.map((message: RoundtableMessage, index: number) => {
              const colors = message.provider
                ? PROVIDER_COLORS[message.provider] || { bg: "bg-gray-500/10", text: "text-gray-400", border: "border-gray-500/30" }
                : { bg: "bg-white/5", text: "text-white", border: "border-white/10" };

              return (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`p-4 rounded-lg border ${colors.border} ${colors.bg}`}
                  data-testid={`message-${message.id}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className={`font-semibold ${colors.text}`}>
                      {message.senderType === "user"
                        ? "You"
                        : message.senderType === "system"
                        ? "System"
                        : message.provider?.toUpperCase() || "AI"}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {message.tokensUsed && `${message.tokensUsed} tokens`}
                      {message.responseTimeMs && ` • ${(message.responseTimeMs / 1000).toFixed(1)}s`}
                    </span>
                  </div>
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  {message.signature && (
                    <p className="text-xs text-muted-foreground mt-2 italic">{message.signature}</p>
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>

          {messages.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No messages yet. Start the conversation or run an AI round.</p>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="flex gap-2 mt-4 pt-4 border-t border-white/10">
        <Input
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          placeholder="Type your message to the roundtable..."
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && userMessage && sendMessage.mutate()}
          disabled={session.status !== "active"}
          data-testid="input-user-message"
        />
        <Button
          onClick={() => sendMessage.mutate()}
          disabled={!userMessage || sendMessage.isPending || session.status !== "active"}
          data-testid="button-send-message"
        >
          {sendMessage.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </Button>
      </div>
    </div>
  );
}

export default function Roundtable() {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: providers = [] } = useQuery<Provider[]>({
    queryKey: ["/api/roundtable/providers"],
    queryFn: async () => {
      const res = await fetch("/api/roundtable/providers", { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch providers");
      return res.json();
    },
  });

  const { data: sessions = [], isLoading } = useQuery<RoundtableSession[]>({
    queryKey: ["/api/roundtable/sessions"],
    queryFn: async () => {
      const res = await fetch("/api/roundtable/sessions", { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch sessions");
      return res.json();
    },
  });

  if (selectedSessionId) {
    return (
      <Layout>
        <SessionView
          sessionId={selectedSessionId}
          onBack={() => setSelectedSessionId(null)}
        />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2 text-glow" data-testid="text-page-title">
              AI Roundtable
            </h1>
            <p className="text-muted-foreground">
              Collaborative discussions with multiple AI providers working together.
            </p>
          </div>
          <NewSessionDialog
            providers={providers}
            onCreated={() => queryClient.invalidateQueries({ queryKey: ["/api/roundtable/sessions"] })}
          />
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-16 glass-panel rounded-2xl border border-white/5">
            <Users className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="text-xl font-semibold mb-2">No roundtable sessions yet</h3>
            <p className="text-muted-foreground mb-6">
              Create your first AI roundtable to start collaborative discussions.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {sessions.map((session: RoundtableSession, i: number) => (
              <motion.div
                key={session.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="glass-panel p-6 rounded-2xl border border-white/5 cursor-pointer hover:border-white/20 transition-colors"
                onClick={() => setSelectedSessionId(session.id)}
                data-testid={`card-session-${session.id}`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">{session.title}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-1">
                      {session.topic || "No topic set"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={session.status === "active" ? "default" : "secondary"}>
                      {session.status}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      Turn {session.currentTurn}/{session.maxTurns}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-4">
                  {session.activeProviders?.map((providerId: string) => {
                    const colors = PROVIDER_COLORS[providerId] || { bg: "bg-gray-500/10", text: "text-gray-400", border: "border-gray-500/30" };
                    const provider = providers.find((p: Provider) => p.id === providerId);
                    return (
                      <Badge
                        key={providerId}
                        variant="outline"
                        className={`${colors.bg} ${colors.text} ${colors.border}`}
                      >
                        {provider?.name || providerId}
                      </Badge>
                    );
                  })}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
