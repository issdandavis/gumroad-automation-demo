import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Layout from "@/components/dashboard/Layout";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, FileText, Loader2, Calendar, Filter, Eye } from "lucide-react";
import { format } from "date-fns";

interface AuditLog {
  id: string;
  orgId: string;
  userId: string | null;
  action: string;
  target: string;
  detailJson: any;
  createdAt: string;
}

const ACTION_FILTERS = [
  { value: "all", label: "All Actions" },
  { value: "integration", label: "Integration" },
  { value: "credential", label: "Credential" },
  { value: "decision", label: "Decision" },
  { value: "roundtable", label: "Roundtable" },
  { value: "agent", label: "Agent" },
  { value: "admin", label: "Admin" },
  { value: "assistant", label: "Assistant" },
];

const DATE_FILTERS = [
  { value: "all", label: "All Time" },
  { value: "today", label: "Today" },
  { value: "7days", label: "Last 7 Days" },
  { value: "30days", label: "Last 30 Days" },
];

function formatAction(action: string): string {
  return action
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function filterByDateRange(logs: AuditLog[], dateFilter: string): AuditLog[] {
  if (dateFilter === "all") return logs;
  
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  let cutoffDate: Date;
  switch (dateFilter) {
    case "today":
      cutoffDate = startOfToday;
      break;
    case "7days":
      cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      break;
    case "30days":
      cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      break;
    default:
      return logs;
  }
  
  return logs.filter((log) => new Date(log.createdAt) >= cutoffDate);
}

export default function Logs() {
  const [searchQuery, setSearchQuery] = useState("");
  const [actionFilter, setActionFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("all");
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const { data: logs = [], isLoading, error } = useQuery<AuditLog[]>({
    queryKey: ["/api/admin/audit-logs", searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.set("search", searchQuery);
      params.set("limit", "500");
      const res = await fetch(`/api/admin/audit-logs?${params.toString()}`);
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to fetch logs");
      }
      return res.json();
    },
    refetchInterval: 30000,
  });

  const filteredLogs = logs
    .filter((log) => {
      if (actionFilter === "all") return true;
      return log.action.toLowerCase().includes(actionFilter.toLowerCase());
    })
    .filter((log) => filterByDateRange([log], dateFilter).length > 0);

  const paginatedLogs = filteredLogs.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(filteredLogs.length / pageSize);

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2 text-glow" data-testid="text-logs-title">
            Flight Recorder
          </h1>
          <p className="text-muted-foreground" data-testid="text-logs-description">
            Complete audit trail of all system activities and events.
          </p>
        </div>

        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search by action or target..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(0);
                }}
                className="pl-10"
                data-testid="input-search-logs"
              />
            </div>
            <div className="flex gap-2">
              <Select value={actionFilter} onValueChange={(v) => { setActionFilter(v); setPage(0); }}>
                <SelectTrigger className="w-[160px]" data-testid="select-action-filter">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Filter by action" />
                </SelectTrigger>
                <SelectContent>
                  {ACTION_FILTERS.map((filter) => (
                    <SelectItem key={filter.value} value={filter.value}>
                      {filter.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={dateFilter} onValueChange={(v) => { setDateFilter(v); setPage(0); }}>
                <SelectTrigger className="w-[160px]" data-testid="select-date-filter">
                  <Calendar className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Date range" />
                </SelectTrigger>
                <SelectContent>
                  {DATE_FILTERS.map((filter) => (
                    <SelectItem key={filter.value} value={filter.value}>
                      {filter.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-16" data-testid="loader-logs">
              <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="text-center py-16" data-testid="text-logs-error">
              <p className="text-destructive">Failed to load audit logs. Make sure you have admin access.</p>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="text-center py-16" data-testid="text-logs-empty">
              <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="font-medium mb-2">No audit logs found</h3>
              <p className="text-sm text-muted-foreground">
                {searchQuery || actionFilter !== "all" || dateFilter !== "all"
                  ? "Try adjusting your filters"
                  : "Activity will appear here as events occur"}
              </p>
            </div>
          ) : (
            <>
              <ScrollArea className="h-[500px]">
                <Table data-testid="table-logs">
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[180px]">Timestamp</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Target</TableHead>
                      <TableHead className="w-[100px]">Details</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedLogs.map((log) => (
                      <TableRow
                        key={log.id}
                        className="cursor-pointer hover:bg-white/5"
                        onClick={() => setSelectedLog(log)}
                        data-testid={`row-log-${log.id}`}
                      >
                        <TableCell className="font-mono text-xs text-muted-foreground">
                          {format(new Date(log.createdAt), "MMM d, yyyy HH:mm:ss")}
                        </TableCell>
                        <TableCell>
                          <span className="inline-flex items-center px-2 py-1 rounded-md bg-primary/10 text-primary text-xs font-medium">
                            {formatAction(log.action)}
                          </span>
                        </TableCell>
                        <TableCell className="font-mono text-sm truncate max-w-[200px]">
                          {log.target}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedLog(log);
                            }}
                            data-testid={`button-view-details-${log.id}`}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>

              <div className="flex items-center justify-between pt-4 border-t border-white/10">
                <div className="text-sm text-muted-foreground" data-testid="text-logs-count">
                  Showing {page * pageSize + 1} - {Math.min((page + 1) * pageSize, filteredLogs.length)} of {filteredLogs.length} entries
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(Math.max(0, page - 1))}
                    disabled={page === 0}
                    data-testid="button-prev-page"
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                    disabled={page >= totalPages - 1}
                    data-testid="button-next-page"
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>

        <Dialog open={!!selectedLog} onOpenChange={(open) => !open && setSelectedLog(null)}>
          <DialogContent className="max-w-2xl" data-testid="dialog-log-details">
            <DialogHeader>
              <DialogTitle>Audit Log Details</DialogTitle>
            </DialogHeader>
            {selectedLog && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-muted-foreground">Timestamp</label>
                    <p className="font-mono text-sm" data-testid="text-detail-timestamp">
                      {format(new Date(selectedLog.createdAt), "PPpp")}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Action</label>
                    <p className="text-sm font-medium" data-testid="text-detail-action">
                      {formatAction(selectedLog.action)}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Target</label>
                    <p className="font-mono text-sm break-all" data-testid="text-detail-target">
                      {selectedLog.target}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Log ID</label>
                    <p className="font-mono text-xs text-muted-foreground" data-testid="text-detail-id">
                      {selectedLog.id}
                    </p>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Full Details (JSON)</label>
                  <ScrollArea className="h-[300px] mt-2">
                    <pre
                      className="bg-black/30 p-4 rounded-lg text-xs font-mono whitespace-pre-wrap overflow-auto"
                      data-testid="text-detail-json"
                    >
                      {JSON.stringify(selectedLog, null, 2)}
                    </pre>
                  </ScrollArea>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
}
