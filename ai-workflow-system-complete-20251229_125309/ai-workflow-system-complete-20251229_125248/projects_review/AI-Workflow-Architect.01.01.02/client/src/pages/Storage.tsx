import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Layout from "@/components/dashboard/Layout";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Skeleton } from "@/components/ui/skeleton";
import {
  HardDrive,
  Cloud,
  Folder,
  File,
  Download,
  ExternalLink,
  Trash2,
  FolderPlus,
  Search,
  Sparkles,
  ChevronRight,
  FileText,
  FileImage,
  FileArchive,
  FileCode,
  FileVideo,
  FileAudio,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { apiRequest } from "@/lib/queryClient";
import { format } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import { useToast } from "@/hooks/use-toast";

type StorageProvider = "google-drive" | "onedrive" | "dropbox";

interface ProviderStatus {
  provider: StorageProvider;
  connected: boolean;
  name?: string;
  email?: string;
  spaceUsed?: number;
  spaceTotal?: number;
}

interface UnifiedFile {
  id: string;
  name: string;
  path?: string;
  isFolder: boolean;
  size?: number;
  mimeType?: string;
  modifiedAt?: string;
  createdAt?: string;
  webViewLink?: string;
  thumbnailLink?: string;
  provider: StorageProvider;
}

interface BreadcrumbEntry {
  id: string | null;
  name: string;
}

function formatBytes(bytes?: number): string {
  if (!bytes || bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function getFileIcon(file: UnifiedFile) {
  if (file.isFolder) return <Folder className="w-5 h-5 text-yellow-500" />;

  const mimeType = file.mimeType || "";
  const name = file.name.toLowerCase();

  if (mimeType.startsWith("image/") || /\.(jpg|jpeg|png|gif|svg|webp)$/.test(name)) {
    return <FileImage className="w-5 h-5 text-pink-500" />;
  }
  if (mimeType.startsWith("video/") || /\.(mp4|mov|avi|mkv|webm)$/.test(name)) {
    return <FileVideo className="w-5 h-5 text-purple-500" />;
  }
  if (mimeType.startsWith("audio/") || /\.(mp3|wav|ogg|flac)$/.test(name)) {
    return <FileAudio className="w-5 h-5 text-green-500" />;
  }
  if (/\.(zip|rar|7z|tar|gz)$/.test(name)) {
    return <FileArchive className="w-5 h-5 text-orange-500" />;
  }
  if (/\.(js|ts|jsx|tsx|py|java|c|cpp|html|css|json)$/.test(name)) {
    return <FileCode className="w-5 h-5 text-cyan-500" />;
  }
  if (/\.(pdf|doc|docx|txt|md)$/.test(name) || mimeType.includes("document")) {
    return <FileText className="w-5 h-5 text-blue-500" />;
  }

  return <File className="w-5 h-5 text-muted-foreground" />;
}

function getProviderIcon(provider: StorageProvider) {
  switch (provider) {
    case "google-drive":
      return <Cloud className="w-4 h-4" />;
    case "onedrive":
      return <Cloud className="w-4 h-4" />;
    case "dropbox":
      return <HardDrive className="w-4 h-4" />;
  }
}

function getProviderColor(provider: StorageProvider) {
  switch (provider) {
    case "google-drive":
      return { accent: "blue", border: "border-blue-500/20", bg: "bg-blue-500", text: "text-blue-400" };
    case "onedrive":
      return { accent: "sky", border: "border-sky-500/20", bg: "bg-sky-500", text: "text-sky-400" };
    case "dropbox":
      return { accent: "indigo", border: "border-indigo-500/20", bg: "bg-indigo-500", text: "text-indigo-400" };
  }
}

function getProviderName(provider: StorageProvider) {
  switch (provider) {
    case "google-drive":
      return "Google Drive";
    case "onedrive":
      return "OneDrive";
    case "dropbox":
      return "Dropbox";
  }
}

export default function Storage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  const [selectedProvider, setSelectedProvider] = useState<StorageProvider>("google-drive");
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbEntry[]>([{ id: null, name: "Root" }]);
  const [searchQuery, setSearchQuery] = useState("");
  const [aiSearchResult, setAiSearchResult] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [showNewFolderDialog, setShowNewFolderDialog] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<UnifiedFile | null>(null);

  const { data: providersData, isLoading: providersLoading } = useQuery<{ providers: ProviderStatus[] }>({
    queryKey: ["/api/storage/providers"],
  });

  const { data: filesData, isLoading: filesLoading, refetch: refetchFiles } = useQuery<{ files: UnifiedFile[] }>({
    queryKey: ["/api/storage/files", selectedProvider, currentFolderId],
    queryFn: async () => {
      const url = currentFolderId
        ? `/api/storage/files/${selectedProvider}?folderId=${encodeURIComponent(currentFolderId)}`
        : `/api/storage/files/${selectedProvider}`;
      const res = await fetch(url, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch files");
      return res.json();
    },
    enabled: !!selectedProvider,
  });

  const createFolderMutation = useMutation({
    mutationFn: async (name: string) => {
      const res = await apiRequest("POST", `/api/storage/folder/${selectedProvider}`, {
        name,
        parentFolderId: currentFolderId || undefined,
      });
      return res.json();
    },
    onSuccess: () => {
      toast({ title: "Folder created successfully" });
      queryClient.invalidateQueries({ queryKey: ["/api/storage/files", selectedProvider, currentFolderId] });
      setShowNewFolderDialog(false);
      setNewFolderName("");
    },
    onError: (error: Error) => {
      toast({ title: "Failed to create folder", description: error.message, variant: "destructive" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (file: UnifiedFile) => {
      // For Dropbox, use path instead of id since Dropbox API uses paths
      const identifier = file.provider === 'dropbox' && file.path ? file.path : file.id;
      const res = await apiRequest("DELETE", `/api/storage/${file.provider}/${encodeURIComponent(identifier)}`);
      return res.json();
    },
    onSuccess: () => {
      toast({ title: "Item deleted successfully" });
      queryClient.invalidateQueries({ queryKey: ["/api/storage/files", selectedProvider, currentFolderId] });
      setDeleteTarget(null);
    },
    onError: (error: Error) => {
      toast({ title: "Failed to delete item", description: error.message, variant: "destructive" });
    },
  });

  const handleFolderClick = (folder: UnifiedFile) => {
    // For Dropbox, use path as folder identifier since Dropbox API uses paths
    const folderId = folder.provider === 'dropbox' && folder.path ? folder.path : folder.id;
    setCurrentFolderId(folderId);
    setBreadcrumbs((prev) => [...prev, { id: folderId, name: folder.name }]);
  };

  const handleBreadcrumbClick = (index: number) => {
    const target = breadcrumbs[index];
    setCurrentFolderId(target.id);
    setBreadcrumbs(breadcrumbs.slice(0, index + 1));
  };

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider as StorageProvider);
    setCurrentFolderId(null);
    setBreadcrumbs([{ id: null, name: "Root" }]);
    setAiSearchResult(null);
    setSearchQuery("");
  };

  const handleDownload = (file: UnifiedFile) => {
    // For Dropbox, use path instead of id since Dropbox API uses paths
    const identifier = file.provider === 'dropbox' && file.path ? file.path : file.id;
    const url = `/api/storage/download/${file.provider}/${encodeURIComponent(identifier)}`;
    window.open(url, "_blank");
  };

  const handleAiSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setAiSearchResult(null);
    
    try {
      const files = filesData?.files || [];
      const fileList = files.map((f) => `- ${f.name}${f.isFolder ? " (folder)" : ""}`).join("\n");
      
      const prompt = `Given these files in a ${getProviderName(selectedProvider)} storage:
${fileList}

User is searching for: "${searchQuery}"

Help them find relevant files. If you find matches, list them. If not, suggest what they might be looking for. Be concise.`;

      const res = await apiRequest("POST", "/api/gemini/chat", { prompt });
      const data = await res.json();
      setAiSearchResult(data.content);
    } catch (error) {
      toast({ title: "AI search failed", description: "Please try again", variant: "destructive" });
    } finally {
      setIsSearching(false);
    }
  };

  const connectedProviders = providersData?.providers?.filter((p) => p.connected) || [];
  const currentProvider = providersData?.providers?.find((p) => p.provider === selectedProvider);
  const files = filesData?.files || [];

  const sortedFiles = [...files].sort((a, b) => {
    if (a.isFolder && !b.isFolder) return -1;
    if (!a.isFolder && b.isFolder) return 1;
    return a.name.localeCompare(b.name);
  });

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2 text-glow" data-testid="text-page-title">
              Secure Storage Vault
            </h1>
            <p className="text-muted-foreground">
              Unified access to your cloud storage providers.
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetchFiles()}
              className="gap-2"
              data-testid="button-refresh"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </Button>
          </div>
        </div>

        {providersLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-40 rounded-2xl" />
            ))}
          </div>
        ) : connectedProviders.length === 0 ? (
          <div className="glass-panel p-12 rounded-2xl text-center">
            <Cloud className="w-16 h-16 mx-auto mb-4 text-blue-400" />
            <h2 className="text-xl font-semibold mb-2">Connect Your Cloud Storage</h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Link your Google Drive, OneDrive, or Dropbox to access and manage your files from one place.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto mb-6">
              <div className="glass-panel p-4 rounded-xl border border-red-500/20">
                <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-3">
                  <HardDrive className="w-5 h-5 text-red-400" />
                </div>
                <h3 className="font-medium text-sm">Google Drive</h3>
                <p className="text-xs text-muted-foreground mt-1">15 GB free storage</p>
              </div>
              <div className="glass-panel p-4 rounded-xl border border-blue-500/20">
                <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center mx-auto mb-3">
                  <Cloud className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="font-medium text-sm">OneDrive</h3>
                <p className="text-xs text-muted-foreground mt-1">5 GB free storage</p>
              </div>
              <div className="glass-panel p-4 rounded-xl border border-indigo-500/20">
                <div className="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center mx-auto mb-3">
                  <Cloud className="w-5 h-5 text-indigo-400" />
                </div>
                <h3 className="font-medium text-sm">Dropbox</h3>
                <p className="text-xs text-muted-foreground mt-1">2 GB free storage</p>
              </div>
            </div>
            <Button 
              onClick={() => window.location.href = '/integrations'}
              className="gap-2"
              data-testid="button-go-integrations"
            >
              <ExternalLink className="w-4 h-4" />
              Go to Integrations to Connect
            </Button>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {connectedProviders.map((provider) => {
                const colors = getProviderColor(provider.provider);
                const usagePercent =
                  provider.spaceTotal && provider.spaceTotal > 0
                    ? Math.round((provider.spaceUsed || 0) / provider.spaceTotal * 100)
                    : 0;

                return (
                  <motion.div
                    key={provider.provider}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={cn(
                      "glass-panel p-6 rounded-2xl relative overflow-hidden cursor-pointer transition-all",
                      colors.border,
                      selectedProvider === provider.provider && "ring-2 ring-primary"
                    )}
                    onClick={() => handleProviderChange(provider.provider)}
                    data-testid={`card-provider-${provider.provider}`}
                  >
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                      {getProviderIcon(provider.provider)}
                    </div>
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <span className={cn("w-2 h-2 rounded-full", colors.bg)} />
                      {getProviderName(provider.provider)}
                    </h3>
                    {provider.email && (
                      <p className="text-xs text-muted-foreground mb-2 truncate">{provider.email}</p>
                    )}
                    <div className="space-y-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Used Space</span>
                        <span className="font-mono">
                          {formatBytes(provider.spaceUsed)} / {formatBytes(provider.spaceTotal)}
                        </span>
                      </div>
                      <Progress
                        value={usagePercent}
                        className="h-2 bg-white/5"
                      />
                    </div>
                  </motion.div>
                );
              })}
            </div>

            <Tabs
              value={selectedProvider}
              onValueChange={handleProviderChange}
              className="space-y-6"
            >
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <TabsList className="bg-white/5">
                  {connectedProviders.map((p) => (
                    <TabsTrigger
                      key={p.provider}
                      value={p.provider}
                      className="gap-2"
                      data-testid={`tab-${p.provider}`}
                    >
                      {getProviderIcon(p.provider)}
                      {getProviderName(p.provider)}
                    </TabsTrigger>
                  ))}
                </TabsList>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowNewFolderDialog(true)}
                    className="gap-2"
                    data-testid="button-new-folder"
                  >
                    <FolderPlus className="w-4 h-4" />
                    New Folder
                  </Button>
                </div>
              </div>

              <div className="flex gap-2 items-center">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Ask AI to help find files..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAiSearch()}
                    className="pl-10 bg-white/5"
                    data-testid="input-search"
                  />
                </div>
                <Button
                  onClick={handleAiSearch}
                  disabled={isSearching || !searchQuery.trim()}
                  className="gap-2"
                  data-testid="button-ai-search"
                >
                  <Sparkles className="w-4 h-4" />
                  {isSearching ? "Searching..." : "AI Search"}
                </Button>
              </div>

              <AnimatePresence>
                {aiSearchResult && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="glass-panel p-4 rounded-xl border border-purple-500/20"
                  >
                    <div className="flex items-start gap-3">
                      <Sparkles className="w-5 h-5 text-purple-400 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-purple-400 mb-1">AI Search Result</p>
                        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                          {aiSearchResult}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <Breadcrumb>
                <BreadcrumbList>
                  {breadcrumbs.map((crumb, index) => (
                    <BreadcrumbItem key={index}>
                      {index < breadcrumbs.length - 1 ? (
                        <>
                          <BreadcrumbLink
                            onClick={() => handleBreadcrumbClick(index)}
                            className="cursor-pointer hover:text-primary"
                            data-testid={`breadcrumb-${index}`}
                          >
                            {crumb.name}
                          </BreadcrumbLink>
                          <BreadcrumbSeparator>
                            <ChevronRight className="w-4 h-4" />
                          </BreadcrumbSeparator>
                        </>
                      ) : (
                        <BreadcrumbPage>{crumb.name}</BreadcrumbPage>
                      )}
                    </BreadcrumbItem>
                  ))}
                </BreadcrumbList>
              </Breadcrumb>

              {connectedProviders.map((p) => (
                <TabsContent key={p.provider} value={p.provider} className="mt-0">
                  <div className="glass-panel rounded-2xl overflow-hidden">
                    <div className="p-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
                      <h3 className="font-semibold flex items-center gap-2">
                        <Folder className="w-4 h-4 text-primary" />
                        Files
                      </h3>
                      <span className="text-sm text-muted-foreground">
                        {files.length} items
                      </span>
                    </div>

                    {filesLoading ? (
                      <div className="p-4 space-y-2">
                        {[1, 2, 3, 4, 5].map((i) => (
                          <Skeleton key={i} className="h-16 w-full" />
                        ))}
                      </div>
                    ) : sortedFiles.length === 0 ? (
                      <div className="p-12 text-center">
                        <Folder className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                        <p className="text-muted-foreground">This folder is empty</p>
                      </div>
                    ) : (
                      <div className="divide-y divide-white/5">
                        {sortedFiles.map((file) => (
                          <motion.div
                            key={file.id}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className={cn(
                              "p-4 flex items-center justify-between hover:bg-white/5 transition-colors group",
                              file.isFolder && "cursor-pointer"
                            )}
                            onClick={() => file.isFolder && handleFolderClick(file)}
                            data-testid={`file-${file.id}`}
                          >
                            <div className="flex items-center gap-4 min-w-0 flex-1">
                              <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors">
                                {getFileIcon(file)}
                              </div>
                              <div className="min-w-0 flex-1">
                                <div className="font-medium truncate group-hover:text-primary transition-colors">
                                  {file.name}
                                </div>
                                <div className="text-xs text-muted-foreground flex items-center gap-2">
                                  {!file.isFolder && file.size !== undefined && (
                                    <>
                                      <span>{formatBytes(file.size)}</span>
                                      <span className="w-1 h-1 rounded-full bg-white/20" />
                                    </>
                                  )}
                                  {file.modifiedAt && (
                                    <span>
                                      Modified {format(new Date(file.modifiedAt), "MMM d, yyyy")}
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              {file.webViewLink && (
                                <Button
                                  size="icon"
                                  variant="ghost"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    window.open(file.webViewLink, "_blank");
                                  }}
                                  data-testid={`button-view-${file.id}`}
                                >
                                  <ExternalLink className="w-4 h-4" />
                                </Button>
                              )}
                              {!file.isFolder && (
                                <Button
                                  size="icon"
                                  variant="ghost"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDownload(file);
                                  }}
                                  data-testid={`button-download-${file.id}`}
                                >
                                  <Download className="w-4 h-4" />
                                </Button>
                              )}
                              <Button
                                size="icon"
                                variant="ghost"
                                className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setDeleteTarget(file);
                                }}
                                data-testid={`button-delete-${file.id}`}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    )}
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </>
        )}

        <Dialog open={showNewFolderDialog} onOpenChange={setShowNewFolderDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Folder</DialogTitle>
            </DialogHeader>
            <Input
              placeholder="Folder name"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && newFolderName.trim() && createFolderMutation.mutate(newFolderName.trim())}
              data-testid="input-folder-name"
            />
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowNewFolderDialog(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => createFolderMutation.mutate(newFolderName.trim())}
                disabled={!newFolderName.trim() || createFolderMutation.isPending}
                data-testid="button-create-folder"
              >
                {createFolderMutation.isPending ? "Creating..." : "Create"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete {deleteTarget?.isFolder ? "Folder" : "File"}</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete "{deleteTarget?.name}"? This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget)}
                className="bg-red-600 hover:bg-red-700"
                data-testid="button-confirm-delete"
              >
                {deleteMutation.isPending ? "Deleting..." : "Delete"}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </Layout>
  );
}
