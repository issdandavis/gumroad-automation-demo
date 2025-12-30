import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Layout from "@/components/dashboard/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface CircuitStatus {
  isOpen: boolean;
  failures: number;
  openUntil?: string;
}

interface StatusResponse {
  status: string;
  timestamp: string;
  circuits: Record<string, CircuitStatus>;
}

const PROVIDER_LABELS: Record<string, string> = {
  openai: "OpenAI",
  anthropic: "Anthropic",
  google: "Google",
  gemini: "Gemini",
  perplexity: "Perplexity",
  xai: "xAI",
};

export default function Status() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery<StatusResponse>({
    queryKey: ["/api/status"],
    queryFn: async () => {
      const res = await fetch("/api/status");
      if (!res.ok) throw new Error("Failed to fetch status");
      return res.json();
    },
    refetchInterval: 30000,
  });

  const resetMutation = useMutation({
    mutationFn: async (provider?: string) => {
      const res = await fetch("/api/circuits/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to reset circuit");
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/status"] });
      toast({ title: "Circuit reset successfully" });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const handleResetCircuit = (provider: string) => {
    resetMutation.mutate(provider);
  };

  const handleResetAll = () => {
    if (confirm("Are you sure you want to reset all circuit breakers?")) {
      resetMutation.mutate(undefined);
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <AlertCircle className="w-12 h-12 text-destructive" />
          <p className="text-muted-foreground">Failed to load system status</p>
        </div>
      </Layout>
    );
  }

  const providers = Object.entries(data?.circuits || {});

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2 text-glow" data-testid="text-status-title">
              System Status
            </h1>
            <p className="text-muted-foreground">
              Monitor AI provider health and circuit breaker status.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground" data-testid="text-last-updated">
              Last updated: {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : "N/A"}
            </span>
            <Button
              variant="outline"
              onClick={handleResetAll}
              disabled={resetMutation.isPending}
              data-testid="button-reset-all"
            >
              {resetMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Reset All
            </Button>
          </div>
        </div>

        <Card className="glass-panel mb-6" data-testid="card-overall-status">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {data?.status === "ok" ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  <span>System Operational</span>
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5 text-yellow-500" />
                  <span>Degraded Performance</span>
                </>
              )}
            </CardTitle>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providers.map(([provider, circuit]) => (
            <Card key={provider} className="glass-panel" data-testid={`card-provider-${provider}`}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-lg font-medium">
                  {PROVIDER_LABELS[provider] || provider}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <span
                    className={`h-3 w-3 rounded-full ${circuit.isOpen ? "bg-red-500" : "bg-green-500"}`}
                    data-testid={`indicator-${provider}`}
                  />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Circuit Status</span>
                  <Badge
                    variant={circuit.isOpen ? "destructive" : "default"}
                    data-testid={`badge-status-${provider}`}
                  >
                    {circuit.isOpen ? "Open" : "Closed"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Failure Count</span>
                  <span className="font-medium" data-testid={`text-failures-${provider}`}>
                    {circuit.failures}
                  </span>
                </div>
                {circuit.isOpen && circuit.openUntil && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Resets At</span>
                    <span className="text-sm" data-testid={`text-resets-at-${provider}`}>
                      {new Date(circuit.openUntil).toLocaleTimeString()}
                    </span>
                  </div>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => handleResetCircuit(provider)}
                  disabled={resetMutation.isPending}
                  data-testid={`button-reset-${provider}`}
                >
                  Reset Circuit
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {providers.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No provider circuits found
          </div>
        )}
      </div>
    </Layout>
  );
}
