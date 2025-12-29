import Layout from "@/components/dashboard/Layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { motion } from "framer-motion";
import { Plus, Play, Edit, Trash2, Clock, Zap, Webhook, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface WorkflowStep {
  id: string;
  provider: string;
  prompt: string;
}

interface Workflow {
  id: string;
  orgId: string;
  name: string;
  description: string | null;
  trigger: "manual" | "schedule" | "webhook";
  steps: WorkflowStep[];
  status: "active" | "paused" | "draft";
  lastRunAt: string | null;
  runCount: number;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

const TRIGGER_ICONS = {
  manual: Zap,
  schedule: Clock,
  webhook: Webhook,
};

const STATUS_COLORS = {
  active: "bg-green-500/20 text-green-400 border-green-500/30",
  paused: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  draft: "bg-gray-500/20 text-gray-400 border-gray-500/30",
};

const PROVIDERS = [
  { id: "openai", name: "OpenAI (GPT-4o)" },
  { id: "anthropic", name: "Anthropic (Claude)" },
  { id: "google", name: "Google (Gemini)" },
  { id: "xai", name: "xAI (Grok)" },
  { id: "perplexity", name: "Perplexity" },
];

export default function Workflows() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState<Workflow | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    trigger: "manual" as "manual" | "schedule" | "webhook",
    status: "draft" as "active" | "paused" | "draft",
    steps: [{ id: crypto.randomUUID(), provider: "openai", prompt: "" }] as WorkflowStep[],
  });

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: workflows = [], isLoading, error } = useQuery<Workflow[]>({
    queryKey: ["/api/workflows"],
  });

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await fetch("/api/workflows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error((await res.json()).error || "Failed to create workflow");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/workflows"] });
      setIsCreateOpen(false);
      resetForm();
      toast({ title: "Workflow created successfully" });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: typeof formData }) => {
      const res = await fetch(`/api/workflows/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error((await res.json()).error || "Failed to update workflow");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/workflows"] });
      setEditingWorkflow(null);
      resetForm();
      toast({ title: "Workflow updated successfully" });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`/api/workflows/${id}`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!res.ok) throw new Error((await res.json()).error || "Failed to delete workflow");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/workflows"] });
      toast({ title: "Workflow deleted" });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const runMutation = useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`/api/workflows/${id}/run`, {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) throw new Error((await res.json()).error || "Failed to run workflow");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/workflows"] });
      toast({ title: "Workflow started" });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      trigger: "manual",
      status: "draft",
      steps: [{ id: crypto.randomUUID(), provider: "openai", prompt: "" }],
    });
  };

  const openEditDialog = (workflow: Workflow) => {
    setEditingWorkflow(workflow);
    setFormData({
      name: workflow.name,
      description: workflow.description || "",
      trigger: workflow.trigger,
      status: workflow.status,
      steps: workflow.steps.length > 0 ? workflow.steps : [{ id: crypto.randomUUID(), provider: "openai", prompt: "" }],
    });
  };

  const handleSubmit = () => {
    if (!formData.name.trim()) {
      toast({ title: "Name is required", variant: "destructive" });
      return;
    }
    if (formData.steps.length === 0 || !formData.steps[0].prompt.trim()) {
      toast({ title: "At least one step with a prompt is required", variant: "destructive" });
      return;
    }

    if (editingWorkflow) {
      updateMutation.mutate({ id: editingWorkflow.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const addStep = () => {
    setFormData(prev => ({
      ...prev,
      steps: [...prev.steps, { id: crypto.randomUUID(), provider: "openai", prompt: "" }],
    }));
  };

  const removeStep = (stepId: string) => {
    if (formData.steps.length <= 1) return;
    setFormData(prev => ({
      ...prev,
      steps: prev.steps.filter(s => s.id !== stepId),
    }));
  };

  const updateStep = (stepId: string, field: "provider" | "prompt", value: string) => {
    setFormData(prev => ({
      ...prev,
      steps: prev.steps.map(s => s.id === stepId ? { ...s, [field]: value } : s),
    }));
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Never";
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-4xl font-bold tracking-tight mb-2 text-glow" data-testid="workflows-title">
              Workflows
            </h1>
            <p className="text-muted-foreground">
              Build automated AI task sequences that run on demand or on a schedule.
            </p>
          </div>
          <Dialog open={isCreateOpen || !!editingWorkflow} onOpenChange={(open) => {
            if (!open) {
              setIsCreateOpen(false);
              setEditingWorkflow(null);
              resetForm();
            }
          }}>
            <DialogTrigger asChild>
              <Button
                onClick={() => setIsCreateOpen(true)}
                className="gap-2"
                data-testid="button-new-workflow"
              >
                <Plus className="w-4 h-4" />
                New Workflow
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{editingWorkflow ? "Edit Workflow" : "Create New Workflow"}</DialogTitle>
                <DialogDescription>
                  Define your workflow with steps that will be executed in sequence.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-6 py-4">
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      placeholder="My Workflow"
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                      data-testid="input-workflow-name"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      placeholder="What does this workflow do?"
                      value={formData.description}
                      onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                      data-testid="input-workflow-description"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Trigger Type</Label>
                      <Select
                        value={formData.trigger}
                        onValueChange={(value: "manual" | "schedule" | "webhook") => 
                          setFormData(prev => ({ ...prev, trigger: value }))
                        }
                      >
                        <SelectTrigger data-testid="select-workflow-trigger">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="manual">Manual</SelectItem>
                          <SelectItem value="schedule">Scheduled</SelectItem>
                          <SelectItem value="webhook">Webhook</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-2">
                      <Label>Status</Label>
                      <Select
                        value={formData.status}
                        onValueChange={(value: "active" | "paused" | "draft") => 
                          setFormData(prev => ({ ...prev, status: value }))
                        }
                      >
                        <SelectTrigger data-testid="select-workflow-status">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="draft">Draft</SelectItem>
                          <SelectItem value="active">Active</SelectItem>
                          <SelectItem value="paused">Paused</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label className="text-base">Steps</Label>
                    <Button type="button" variant="outline" size="sm" onClick={addStep} data-testid="button-add-step">
                      <Plus className="w-4 h-4 mr-1" /> Add Step
                    </Button>
                  </div>
                  {formData.steps.map((step, index) => (
                    <Card key={step.id} className="relative">
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-sm font-medium">Step {index + 1}</CardTitle>
                          {formData.steps.length > 1 && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={() => removeStep(step.id)}
                              data-testid={`button-remove-step-${index}`}
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="grid gap-2">
                          <Label>AI Provider</Label>
                          <Select
                            value={step.provider}
                            onValueChange={(value) => updateStep(step.id, "provider", value)}
                          >
                            <SelectTrigger data-testid={`select-step-provider-${index}`}>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {PROVIDERS.map(p => (
                                <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid gap-2">
                          <Label>Prompt</Label>
                          <Textarea
                            placeholder="Enter the prompt for this step..."
                            value={step.prompt}
                            onChange={(e) => updateStep(step.id, "prompt", e.target.value)}
                            data-testid={`input-step-prompt-${index}`}
                          />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsCreateOpen(false);
                    setEditingWorkflow(null);
                    resetForm();
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSubmit}
                  disabled={createMutation.isPending || updateMutation.isPending}
                  data-testid="button-save-workflow"
                >
                  {createMutation.isPending || updateMutation.isPending ? "Saving..." : (editingWorkflow ? "Update" : "Create")}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : error ? (
          <Card className="border-destructive">
            <CardContent className="flex items-center gap-4 py-6">
              <AlertCircle className="w-8 h-8 text-destructive" />
              <div>
                <CardTitle className="text-destructive">Failed to load workflows</CardTitle>
                <CardDescription>Please try refreshing the page.</CardDescription>
              </div>
            </CardContent>
          </Card>
        ) : workflows.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <div className="rounded-full bg-primary/10 p-4 mb-4">
                <Zap className="w-8 h-8 text-primary" />
              </div>
              <CardTitle className="mb-2">No workflows yet</CardTitle>
              <CardDescription className="mb-4">
                Create your first workflow to automate AI tasks.
              </CardDescription>
              <Button onClick={() => setIsCreateOpen(true)} data-testid="button-create-first-workflow">
                <Plus className="w-4 h-4 mr-2" /> Create Workflow
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workflows.map((workflow, index) => {
              const TriggerIcon = TRIGGER_ICONS[workflow.trigger];
              return (
                <motion.div
                  key={workflow.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className="glass-card hover:border-primary/50 transition-colors" data-testid={`card-workflow-${workflow.id}`}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <TriggerIcon className="w-4 h-4 text-muted-foreground" />
                          <CardTitle className="text-lg">{workflow.name}</CardTitle>
                        </div>
                        <Badge className={STATUS_COLORS[workflow.status]} data-testid={`badge-status-${workflow.id}`}>
                          {workflow.status}
                        </Badge>
                      </div>
                      {workflow.description && (
                        <CardDescription className="line-clamp-2">
                          {workflow.description}
                        </CardDescription>
                      )}
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                        <span>{workflow.steps.length} step{workflow.steps.length !== 1 ? "s" : ""}</span>
                        <span>Run {workflow.runCount}x</span>
                      </div>
                      <div className="text-xs text-muted-foreground mb-4">
                        Last run: {formatDate(workflow.lastRunAt)}
                      </div>
                      <div className="flex gap-2">
                        {workflow.trigger === "manual" && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => runMutation.mutate(workflow.id)}
                            disabled={runMutation.isPending}
                            data-testid={`button-run-${workflow.id}`}
                          >
                            <Play className="w-3 h-3 mr-1" />
                            Run
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => openEditDialog(workflow)}
                          data-testid={`button-edit-${workflow.id}`}
                        >
                          <Edit className="w-3 h-3 mr-1" />
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-destructive hover:text-destructive"
                          onClick={() => deleteMutation.mutate(workflow.id)}
                          disabled={deleteMutation.isPending}
                          data-testid={`button-delete-${workflow.id}`}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </Layout>
  );
}
