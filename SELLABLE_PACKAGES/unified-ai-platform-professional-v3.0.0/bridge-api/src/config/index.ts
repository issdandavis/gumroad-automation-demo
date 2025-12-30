/**
 * Unified Configuration Management for Bridge API
 */

import { config } from 'dotenv';
import Joi from 'joi';
import { UnifiedConfig, ConfigurationError } from '../types';

// Load environment variables
config();

// Configuration schema validation
const configSchema = Joi.object({
  // Bridge API Configuration
  PORT: Joi.number().default(3001),
  NODE_ENV: Joi.string().valid('development', 'production', 'test').default('development'),
  
  // Redis Configuration
  REDIS_HOST: Joi.string().default('localhost'),
  REDIS_PORT: Joi.number().default(6379),
  REDIS_PASSWORD: Joi.string().optional(),
  REDIS_DB: Joi.number().default(0),
  
  // Evolution Framework Integration
  EVOLUTION_API_URL: Joi.string().uri().default('http://localhost:5000'),
  EVOLUTION_API_KEY: Joi.string().optional(),
  
  // Workflow Orchestrator Integration
  WORKFLOW_API_URL: Joi.string().uri().default('http://localhost:3000'),
  WORKFLOW_API_KEY: Joi.string().optional(),
  
  // Database Configuration
  DATABASE_URL: Joi.string().uri().required(),
  
  // Security
  JWT_SECRET: Joi.string().min(32).required(),
  ENCRYPTION_KEY: Joi.string().length(32).required(),
  
  // Monitoring
  LOG_LEVEL: Joi.string().valid('debug', 'info', 'warn', 'error').default('info'),
  ENABLE_METRICS: Joi.boolean().default(true),
  METRICS_PORT: Joi.number().default(9090),
  
  // Cross-System Configuration
  EVENT_BUS_ENABLED: Joi.boolean().default(true),
  CONFIG_SYNC_ENABLED: Joi.boolean().default(true),
  HEALTH_CHECK_INTERVAL: Joi.number().default(30000),
});

// Validate environment variables
const { error, value: env } = configSchema.validate(process.env, {
  allowUnknown: true,
  stripUnknown: true
});

if (error) {
  throw new ConfigurationError(`Configuration validation failed: ${error.message}`);
}

// Create unified configuration object
export const unifiedConfig: UnifiedConfig = {
  evolution: {
    apiUrl: env.EVOLUTION_API_URL,
    apiKey: env.EVOLUTION_API_KEY,
    healthCheckInterval: env.HEALTH_CHECK_INTERVAL,
    mutationThreshold: 0.1, // Default mutation threshold
    fitnessTargets: {
      overall: 100,
      performance: 90,
      reliability: 95,
      efficiency: 85
    }
  },
  
  workflow: {
    apiUrl: env.WORKFLOW_API_URL,
    apiKey: env.WORKFLOW_API_KEY,
    healthCheckInterval: env.HEALTH_CHECK_INTERVAL,
    maxConcurrentWorkflows: 10,
    agentDefaults: {
      temperature: 0.7,
      maxTokens: 4000,
      timeout: 30000
    }
  },
  
  bridge: {
    port: env.PORT,
    cors: {
      origin: env.NODE_ENV === 'production' 
        ? ['https://your-domain.com'] 
        : ['http://localhost:3000', 'http://localhost:5173'],
      credentials: true
    },
    rateLimit: {
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100 // limit each IP to 100 requests per windowMs
    },
    websocket: {
      enabled: true,
      heartbeatInterval: 30000
    }
  },
  
  shared: {
    database: {
      url: env.DATABASE_URL,
      maxConnections: 20,
      ssl: env.NODE_ENV === 'production'
    },
    redis: {
      host: env.REDIS_HOST,
      port: env.REDIS_PORT,
      password: env.REDIS_PASSWORD,
      db: env.REDIS_DB
    },
    security: {
      jwtSecret: env.JWT_SECRET,
      encryptionKey: env.ENCRYPTION_KEY,
      sessionTimeout: 24 * 60 * 60 * 1000 // 24 hours
    },
    monitoring: {
      logLevel: env.LOG_LEVEL as 'debug' | 'info' | 'warn' | 'error',
      enableMetrics: env.ENABLE_METRICS,
      metricsPort: env.METRICS_PORT
    }
  }
};

// Configuration validation functions
export function validateConfig(config: Partial<UnifiedConfig>): boolean {
  try {
    // Add custom validation logic here
    if (config.evolution?.apiUrl && !isValidUrl(config.evolution.apiUrl)) {
      throw new ConfigurationError('Invalid Evolution API URL');
    }
    
    if (config.workflow?.apiUrl && !isValidUrl(config.workflow.apiUrl)) {
      throw new ConfigurationError('Invalid Workflow API URL');
    }
    
    return true;
  } catch (error) {
    console.error('Configuration validation failed:', error);
    return false;
  }
}

export function mergeConfigs(base: UnifiedConfig, override: Partial<UnifiedConfig>): UnifiedConfig {
  return {
    evolution: { ...base.evolution, ...override.evolution },
    workflow: { ...base.workflow, ...override.workflow },
    bridge: { ...base.bridge, ...override.bridge },
    shared: { ...base.shared, ...override.shared }
  };
}

// Helper functions
function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// Export environment info
export const isDevelopment = env.NODE_ENV === 'development';
export const isProduction = env.NODE_ENV === 'production';
export const isTest = env.NODE_ENV === 'test';

// Configuration hot-reloading support
export class ConfigManager {
  private static instance: ConfigManager;
  private config: UnifiedConfig;
  private watchers: Array<(config: UnifiedConfig) => void> = [];

  private constructor() {
    this.config = unifiedConfig;
  }

  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  getConfig(): UnifiedConfig {
    return { ...this.config };
  }

  updateConfig(updates: Partial<UnifiedConfig>): void {
    if (!validateConfig(updates)) {
      throw new ConfigurationError('Invalid configuration updates');
    }

    this.config = mergeConfigs(this.config, updates);
    this.notifyWatchers();
  }

  onConfigChange(callback: (config: UnifiedConfig) => void): void {
    this.watchers.push(callback);
  }

  private notifyWatchers(): void {
    this.watchers.forEach(callback => {
      try {
        callback(this.config);
      } catch (error) {
        console.error('Error in config change callback:', error);
      }
    });
  }
}

export default unifiedConfig;