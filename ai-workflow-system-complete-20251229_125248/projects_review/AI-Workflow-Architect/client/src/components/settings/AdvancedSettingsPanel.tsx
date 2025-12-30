import React, { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  Settings, 
  Shield, 
  Zap, 
  Brain, 
  Database, 
  Globe, 
  Lock,
  AlertTriangle,
  CheckCircle,
  Save,
  RotateCcw
} from "lucide-react";

interface SettingsSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  description: string;
}

export function AdvancedSettingsPanel() {
  const [activeSection, setActiveSection] = useState("security");
  const [settings, setSettings] = useState({
    // Security Settings
    encryptionEnabled: true,
    twoFactorAuth: false,
    sessionTimeout: 30,
    auditLogging: true,
    
    // Performance Settings
    maxConcurrentAgents: 5,
    requestTimeout: 30,
    cacheEnabled: true,
    compressionLevel: 6,
    
    // AI Settings
    defaultModel: "claude-3.5-sonnet",
    temperature: 0.7,
    maxTokens: 4000,
    fallbackEnabled: true,
    
    // Integration Settings
    webhooksEnabled: true,
    rateLimitPerMinute: 100,
    retryAttempts: 3,
    batchProcessing: false
  });

  const sections: SettingsSection[] = [
    {
      id: "security",
      title: "Security & Privacy",
      icon: <Shield className="w-5 h-5" />,
      description: "Encryption, authentication, and audit settings"
    },
    {
      id: "performance",
      title: "Performance",
      icon: <Zap className="w-5 h-5" />,
      description: "System optimization and resource management"
    },
    {
      id: "ai",
      title: "AI Configuration",
      icon: <Brain className="w-5 h-5" />,
      description: "Model settings and behavior parameters"
    },
    {
      id: "integrations",
      title: "Integrations",
      icon: <Globe className="w-5 h-5" />,
      description: "External services and API configurations"
    }
  ];

  const updateSetting = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Label className="text-base font-medium">End-to-End Encryption</Label>
          <p className="text-sm text-muted-foreground">
            Encrypt all data with AES-256-GCM
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Switch 
            checked={settings.encryptionEnabled}
            onCheckedChange={(checked) => updateSetting("encryptionEnabled", checked)}
          />
          <Badge variant={settings.encryptionEnabled ? "default" : "secondary"}>
            {settings.encryptionEnabled ? "Active" : "Disabled"}
          </Badge>
        </div>
      </div>

      <Separator />

      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Label className="text-base font-medium">Two-Factor Authentication</Label>
          <p className="text-sm text-muted-foreground">
            Require 2FA for all admin actions
          </p>
        </div>
        <Switch 
          checked={settings.twoFactorAuth}
          onCheckedChange={(checked) => updateSetting("twoFactorAuth", checked)}
        />
      </div>

      <div className="space-y-3">
        <Label className="text-base font-medium">Session Timeout (minutes)</Label>
        <div className="px-3">
          <Slider
            value={[settings.sessionTimeout]}
            onValueChange={([value]) => updateSetting("sessionTimeout", value)}
            max={120}
            min={5}
            step={5}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>5 min</span>
            <span className="font-mono">{settings.sessionTimeout} min</span>
            <span>120 min</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Label className="text-base font-medium">Audit Logging</Label>
          <p className="text-sm text-muted-foreground">
            Log all system activities and changes
          </p>
        </div>
        <Switch 
          checked={settings.auditLogging}
          onCheckedChange={(checked) => updateSetting("auditLogging", checked)}
        />
      </div>
    </div>
  );

  const renderPerformanceSettings = () => (
    <div className="space-y-6">
      <div className="space-y-3">
        <Label className="text-base font-medium">Max Concurrent Agents</Label>
        <div className="px-3">
          <Slider
            value={[settings.maxConcurrentAgents]}
            onValueChange={([value]) => updateSetting("maxConcurrentAgents", value)}
            max={20}
            min={1}
            step={1}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>1 agent</span>
            <span className="font-mono">{settings.maxConcurrentAgents} agents</span>
            <span>20 agents</span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <Label className="text-base font-medium">Request Timeout (seconds)</Label>
        <Input
          type="number"
          value={settings.requestTimeout}
          onChange={(e) => updateSetting("requestTimeout", parseInt(e.target.value))}
          min={5}
          max={300}
          className="w-32"
        />
      </div>

      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Label className="text-base font-medium">Response Caching</Label>
          <p className="text-sm text-muted-foreground">
            Cache API responses to improve performance
          </p>
        </div>
        <Switch 
          checked={settings.cacheEnabled}
          onCheckedChange={(checked) => updateSetting("cacheEnabled", checked)}
        />
      </div>

      <div className="space-y-3">
        <Label className="text-base font-medium">Compression Level</Label>
        <div className="px-3">
          <Slider
            value={[settings.compressionLevel]}
            onValueChange={([value]) => updateSetting("compressionLevel", value)}
            max={9}
            min={0}
            step={1}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>None</span>
            <span className="font-mono">Level {settings.compressionLevel}</span>
            <span>Max</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAISettings = () => (
    <div className="space-y-6">
      <div className="space-y-3">
        <Label className="text-base font-medium">Default AI Model</Label>
        <select 
          value={settings.defaultModel}
          onChange={(e) => updateSetting("defaultModel", e.target.value)}
          className="w-full p-2 rounded-md border border-input bg-background"
        >
          <option value="claude-3.5-sonnet">Claude 3.5 Sonnet</option>
          <option value="gpt-4o">GPT-4o</option>
          <option value="grok-beta">Grok Beta</option>
          <option value="gemini-pro">Gemini Pro</option>
        </select>
      </div>

      <div className="space-y-3">
        <Label className="text-base font-medium">Temperature</Label>
        <div className="px-3">
          <Slider
            value={[settings.temperature]}
            onValueChange={([value]) => updateSetting("temperature", value)}
            max={2}
            min={0}
            step={0.1}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>Focused</span>
            <span className="font-mono">{settings.temperature}</span>
            <span>Creative</span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <Label className="text-base font-medium">Max Tokens</Label>
        <Input
          type="number"
          value={settings.maxTokens}
          onChange={(e) => updateSetting("maxTokens", parseInt(e.target.value))}
          min={100}
          max={32000}
          className="w-32"
        />
      </div>

      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Label className="text-base font-medium">Automatic Fallback</Label>
          <p className="text-sm text-muted-foreground">
            Switch to backup model if primary fails
          </p>
        </div>
        <Switch 
          checked={settings.fallbackEnabled}
          onCheckedChange={(checked) => updateSetting("fallbackEnabled", checked)}
        />
      </div>
    </div>
  );

  const renderIntegrationSettings = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Label className="text-base font-medium">Webhook Notifications</Label>
          <p className="text-sm text-muted-foreground">
            Send events to external services
          </p>
        </div>
        <Switch 
          checked={settings.webhooksEnabled}
          onCheckedChange={(checked) => updateSetting("webhooksEnabled", checked)}
        />
      </div>

      <div className="space-y-3">
        <Label className="text-base font-medium">Rate Limit (requests/minute)</Label>
        <Input
          type="number"
          value={settings.rateLimitPerMinute}
          onChange={(e) => updateSetting("rateLimitPerMinute", parseInt(e.target.value))}
          min={10}
          max={1000}
          className="w-32"
        />
      </div>

      <div className="space-y-3">
        <Label className="text-base font-medium">Retry Attempts</Label>
        <Input
          type="number"
          value={settings.retryAttempts}
          onChange={(e) => updateSetting("retryAttempts", parseInt(e.target.value))}
          min={0}
          max={10}
          className="w-32"
        />
      </div>

      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Label className="text-base font-medium">Batch Processing</Label>
          <p className="text-sm text-muted-foreground">
            Process multiple requests together
          </p>
        </div>
        <Switch 
          checked={settings.batchProcessing}
          onCheckedChange={(checked) => updateSetting("batchProcessing", checked)}
        />
      </div>
    </div>
  );

  const renderSettingsContent = () => {
    switch (activeSection) {
      case "security":
        return renderSecuritySettings();
      case "performance":
        return renderPerformanceSettings();
      case "ai":
        return renderAISettings();
      case "integrations":
        return renderIntegrationSettings();
      default:
        return renderSecuritySettings();
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 h-full">
      {/* Settings Navigation */}
      <div className="lg:col-span-1">
        <Card className="glass-panel h-fit">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {sections.map((section) => (
              <motion.button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`w-full p-3 rounded-lg text-left transition-all ${
                  activeSection === section.id
                    ? "bg-primary/20 border border-primary/30 text-primary"
                    : "hover:bg-muted/50 border border-transparent"
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center gap-3 mb-1">
                  {section.icon}
                  <span className="font-medium">{section.title}</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  {section.description}
                </p>
              </motion.button>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Settings Content */}
      <div className="lg:col-span-3">
        <Card className="glass-panel">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  {sections.find(s => s.id === activeSection)?.icon}
                  {sections.find(s => s.id === activeSection)?.title}
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {sections.find(s => s.id === activeSection)?.description}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Saved
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <motion.div
              key={activeSection}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              {renderSettingsContent()}
            </motion.div>

            <Separator className="my-8" />

            {/* Action Buttons */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Lock className="w-4 h-4" />
                <span>Changes are automatically encrypted and saved</span>
              </div>
              
              <div className="flex items-center gap-3">
                <Button variant="outline" className="gap-2">
                  <RotateCcw className="w-4 h-4" />
                  Reset to Defaults
                </Button>
                <Button className="gap-2">
                  <Save className="w-4 h-4" />
                  Save Changes
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}