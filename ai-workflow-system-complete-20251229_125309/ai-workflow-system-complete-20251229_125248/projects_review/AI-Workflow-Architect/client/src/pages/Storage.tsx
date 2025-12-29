
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
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { HardDrive, Cloud, Folder, File, Download, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import bgImage from "@assets/generated_images/futuristic_secure_data_vault_background_for_backend_portal.png";

export default function Storage() {
  const files = [
    { name: "Project_Specs_v2.pdf", size: "2.4 MB", type: "pdf", source: "Dropbox" },
    { name: "Design_Assets_2025.zip", size: "156 MB", type: "zip", source: "Google Drive" },
    { name: "Client_Database_Backup.sql", size: "45 MB", type: "sql", source: "Google Drive" },
    { name: "Marketing_Brief.docx", size: "1.2 MB", type: "doc", source: "Dropbox" },
  ];

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2 text-glow">Secure Storage Vault</h1>
            <p className="text-muted-foreground">Unified access to your Dropbox and Google Drive repositories.</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="gap-2 border-blue-500/30 text-blue-400 hover:bg-blue-500/10">
              <Cloud className="w-4 h-4" /> Connect New Drive
            </Button>
          </div>
        </div>

        {/* Storage Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-panel p-6 rounded-2xl border-blue-500/20 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <Cloud className="w-24 h-24" />
            </div>
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              Google Drive
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Used Space</span>
                <span className="font-mono">45.2 GB / 100 GB</span>
              </div>
              <Progress value={45} className="h-2 bg-blue-950" indicatorClassName="bg-blue-500" />
              <div className="pt-2">
                 <Button size="sm" variant="ghost" className="w-full justify-between hover:bg-blue-500/10 hover:text-blue-400 group">
                   Open Drive <ExternalLink className="w-4 h-4 opacity-50 group-hover:opacity-100" />
                 </Button>
              </div>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border-indigo-500/20 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <HardDrive className="w-24 h-24" />
            </div>
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500" />
              Dropbox
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Used Space</span>
                <span className="font-mono">12.8 GB / 50 GB</span>
              </div>
              <Progress value={25} className="h-2 bg-indigo-950" indicatorClassName="bg-indigo-500" />
              <div className="pt-2">
                 <Button size="sm" variant="ghost" className="w-full justify-between hover:bg-indigo-500/10 hover:text-indigo-400 group">
                   Open Dropbox <ExternalLink className="w-4 h-4 opacity-50 group-hover:opacity-100" />
                 </Button>
              </div>
            </div>
          </div>
        </div>

        {/* File Browser */}
        <div className="glass-panel rounded-2xl overflow-hidden">
          <div className="p-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
            <h3 className="font-semibold flex items-center gap-2">
              <Folder className="w-4 h-4 text-primary" />
              Recent Files
            </h3>
            <Button size="sm" variant="ghost">View All</Button>
          </div>
          
          <div className="divide-y divide-white/5">
            {files.map((file, i) => (
              <div key={i} className="p-4 flex items-center justify-between hover:bg-white/5 transition-colors group">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-muted-foreground group-hover:text-primary transition-colors">
                    <File className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-medium group-hover:text-primary transition-colors">{file.name}</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-2">
                      <span>{file.size}</span>
                      <span className="w-1 h-1 rounded-full bg-white/20" />
                      <span className={cn(
                        "flex items-center gap-1",
                        file.source === "Google Drive" ? "text-blue-400" : "text-indigo-400"
                      )}>
                        {file.source === "Google Drive" ? <Cloud className="w-3 h-3" /> : <HardDrive className="w-3 h-3" />}
                        {file.source}
                      </span>
                    </div>
                  </div>
                </div>
                <Button size="icon" variant="ghost" className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <Download className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
