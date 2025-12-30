/**
 * Core type definitions for the Unified AI Platform Bridge API
 */

// Cross-System Event Types
export interface CrossSystemEvent {
  id: string;
  type: EventType;
  source: 'evolution' | 'workflow';
  target: 'evolution' | 'workflow' | 'both';
  payload: any;
  timestamp: Date;
  correlationId?: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
}

export enum EventType {
  // Evolution System Events
  MUTATION_APPLIED = 'mutation_applied',
  MUTATION_PROPOSED = 'mutation_proposed',
  FITNESS_CALCULATED = 'fitness_calculated',
  SYSTEM_EVOLVED = 'system_evolved',
  HEALING_COMPLETED = 'healing_completed',
  
  // Workflow System Events
  WORKFLOW_STARTED = 'workflow_started',
  WORKFLOW_COMPLETED = 'workflow_completed',
  AGENT_CONFIGURED = 'agent_configured',
  AGENT_PERFORMANCE_UPDATED = 'agent_performance_updated',
  
  // Cross-System Events
  PERFORMANCE_THRESHOLD = 'performance_threshold',
  SYSTEM_HEALING = 'system_healing',
  OPTIMIZATION_SUGGESTED = 'optimization_suggested',
  CONFIGURATION_SYNCED = 'configuration_synced',
  
  // System Events
  SYSTEM_STARTED = 'system_started',
  SYSTEM_STOPPED = 'system_stopped',
  HEALTH_CHECK = 'health_check'
}

// Unified System Status
export interface UnifiedSystemStatus {
  bridge: {
    version: string;
    uptime: number;
    status: 'healthy' | 'degraded' | 'unhealthy';
    lastHealthCheck: Date;
  };
  evolution: {
    connected: boolean;
    version?: string;
    generation?: number;
    fitnessScore?: number;
    status?: 'running' | 'stopped' | 'error';
  };
  workflow: {
    connected: boolean;
    version?: string;
    activeAgents?: number;
    runningWorkflows?: number;
    status?: 'running' | 'stopped' | 'error';
  };
  integration: {
    eventsSynced: number;
    lastSyncTime: Date;
    configurationSynced: boolean;
    crossSystemOptimizations: number;
  };
}

// Configuration Types
export interface UnifiedConfig {
  evolution: EvolutionConfig;
  workflow: WorkflowConfig;
  bridge: BridgeConfig;
  shared: SharedConfig;
}

export interface EvolutionConfig {
  apiUrl: string;
  apiKey?: string;
  healthCheckInterval: number;
  mutationThreshold: number;
  fitnessTargets: Record<string, number>;
}

export interface WorkflowConfig {
  apiUrl: string;
  apiKey?: string;
  healthCheckInterval: number;
  maxConcurrentWorkflows: number;
  agentDefaults: Record<string, any>;
}

export interface BridgeConfig {
  port: number;
  cors: {
    origin: string[];
    credentials: boolean;
  };
  rateLimit: {
    windowMs: number;
    max: number;
  };
  websocket: {
    enabled: boolean;
    heartbeatInterval: number;
  };
}

export interface SharedConfig {
  database: {
    url: string;
    maxConnections: number;
    ssl: boolean;
  };
  redis: {
    host: string;
    port: number;
    password?: string;
    db: number;
  };
  security: {
    jwtSecret: string;
    encryptionKey: string;
    sessionTimeout: number;
  };
  monitoring: {
    logLevel: 'debug' | 'info' | 'warn' | 'error';
    enableMetrics: boolean;
    metricsPort: number;
  };
}

// Cross-System Optimization Types
export interface CrossSystemOptimization {
  id: string;
  type: 'workflow_evolution' | 'evolution_workflow';
  source: OptimizationSource;
  target: OptimizationTarget;
  recommendations: Recommendation[];
  status: 'pending' | 'applied' | 'rejected';
  impact: ImpactMetrics;
  createdAt: Date;
  appliedAt?: Date;
}

export interface OptimizationSource {
  system: 'evolution' | 'workflow';
  component: string;
  metrics: Record<string, number>;
  context: Record<string, any>;
}

export interface OptimizationTarget {
  system: 'evolution' | 'workflow';
  component: string;
  parameters: Record<string, any>;
}

export interface Recommendation {
  id: string;
  type: 'configuration' | 'parameter' | 'strategy';
  description: string;
  changes: Record<string, any>;
  confidence: number;
  expectedImpact: number;
}

export interface ImpactMetrics {
  performance: number;
  efficiency: number;
  cost: number;
  reliability: number;
  overall: number;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: Date;
  requestId: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Health Check Types
export interface HealthCheck {
  service: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: Date;
  responseTime: number;
  details?: Record<string, any>;
}

// Metrics Types
export interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: {
    bytesIn: number;
    bytesOut: number;
  };
  requests: {
    total: number;
    successful: number;
    failed: number;
    averageResponseTime: number;
  };
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'event' | 'status' | 'metrics' | 'error';
  payload: any;
  timestamp: Date;
  id: string;
}

// Error Types
export class BridgeAPIError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: any
  ) {
    super(message);
    this.name = 'BridgeAPIError';
  }
}

export class IntegrationError extends BridgeAPIError {
  constructor(message: string, public system: 'evolution' | 'workflow', details?: any) {
    super(message, 'INTEGRATION_ERROR', 502, details);
    this.name = 'IntegrationError';
  }
}

export class ConfigurationError extends BridgeAPIError {
  constructor(message: string, details?: any) {
    super(message, 'CONFIGURATION_ERROR', 400, details);
    this.name = 'ConfigurationError';
  }
}