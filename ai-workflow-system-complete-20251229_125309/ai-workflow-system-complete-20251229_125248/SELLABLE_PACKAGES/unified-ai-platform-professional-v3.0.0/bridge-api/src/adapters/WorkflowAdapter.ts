/**
 * Workflow Orchestrator Adapter
 * Handles communication with the AI Workflow Architect
 */

import axios, { AxiosInstance } from 'axios';
import { EventBusService } from '../services/EventBus';
import { Logger } from '../services/Logger';
import { unifiedConfig } from '../config';
import { IntegrationError } from '../types';

export class WorkflowAdapter {
  private httpClient: AxiosInstance;
  private eventBus: EventBusService;
  private logger: Logger;
  private baseUrl: string;

  constructor(eventBus: EventBusService) {
    this.eventBus = eventBus;
    this.logger = new Logger('WorkflowAdapter');
    this.baseUrl = unifiedConfig.workflow.apiUrl;

    this.httpClient = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        ...(unifiedConfig.workflow.apiKey && {
          'Authorization': `Bearer ${unifiedConfig.workflow.apiKey}`
        })
      }
    });

    // Set up request/response interceptors
    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.httpClient.interceptors.request.use(
      (config) => {
        this.logger.debug(`Workflow API request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        this.logger.error('Workflow API request error:', error);
        return Promise.reject(error);
      }
    );

    this.httpClient.interceptors.response.use(
      (response) => {
        this.logger.debug(`Workflow API response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        this.logger.error('Workflow API response error:', error.response?.status, error.message);
        return Promise.reject(error);
      }
    );
  }

  // Status and Health

  async getStatus(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/status');
      return {
        connected: true,
        ...response.data
      };
    } catch (error) {
      this.logger.warn('Workflow Orchestrator not reachable:', error.message);
      return {
        connected: false,
        error: error.message
      };
    }
  }

  async getHealth(): Promise<any> {
    try {
      const response = await this.httpClient.get('/health');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Workflow Orchestrator health check failed',
        'workflow',
        error
      );
    }
  }

  // Workflow Operations

  async executeWorkflow(workflow: any): Promise<any> {
    try {
      const response = await this.httpClient.post('/api/workflows/execute', workflow);
      
      // Publish workflow started event
      await this.eventBus.publishWorkflowEvent(
        'WORKFLOW_STARTED' as any,
        {
          workflow_id: response.data.workflow_id,
          workflow_name: workflow.name,
          agent_count: workflow.agents?.length || 0
        }
      );

      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to execute workflow',
        'workflow',
        error
      );
    }
  }

  async getWorkflowStatus(workflowId: string): Promise<any> {
    try {
      const response = await this.httpClient.get(`/api/workflows/${workflowId}/status`);
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get workflow status',
        'workflow',
        error
      );
    }
  }

  async stopWorkflow(workflowId: string): Promise<any> {
    try {
      const response = await this.httpClient.post(`/api/workflows/${workflowId}/stop`);
      
      // Publish workflow stopped event
      await this.eventBus.publishWorkflowEvent(
        'WORKFLOW_COMPLETED' as any,
        {
          workflow_id: workflowId,
          status: 'stopped',
          reason: 'manual_stop'
        }
      );

      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to stop workflow',
        'workflow',
        error
      );
    }
  }

  async getWorkflowHistory(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/workflows/history');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get workflow history',
        'workflow',
        error
      );
    }
  }

  // Agent Operations

  async configureAgent(agentConfig: any): Promise<any> {
    try {
      const response = await this.httpClient.post('/api/agents/configure', agentConfig);
      
      // Publish agent configured event
      await this.eventBus.publishWorkflowEvent(
        'AGENT_CONFIGURED' as any,
        {
          agent_id: response.data.agent_id,
          agent_type: agentConfig.type,
          configuration: agentConfig
        }
      );

      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to configure agent',
        'workflow',
        error
      );
    }
  }

  async getAgentStatus(agentId: string): Promise<any> {
    try {
      const response = await this.httpClient.get(`/api/agents/${agentId}/status`);
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get agent status',
        'workflow',
        error
      );
    }
  }

  async updateAgentPerformance(agentId: string, metrics: any): Promise<any> {
    try {
      const response = await this.httpClient.post(`/api/agents/${agentId}/performance`, metrics);
      
      // Publish agent performance updated event
      await this.eventBus.publishWorkflowEvent(
        'AGENT_PERFORMANCE_UPDATED' as any,
        {
          agent_id: agentId,
          metrics,
          timestamp: new Date()
        }
      );

      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to update agent performance',
        'workflow',
        error
      );
    }
  }

  async getAgentList(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/agents');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get agent list',
        'workflow',
        error
      );
    }
  }

  // Metrics and Analytics

  async getMetrics(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/metrics');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get workflow metrics',
        'workflow',
        error
      );
    }
  }

  async getPerformanceData(timeRange: string = '24h'): Promise<any> {
    try {
      const response = await this.httpClient.get(`/api/performance?range=${timeRange}`);
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get performance data',
        'workflow',
        error
      );
    }
  }

  async getDashboardData(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/dashboard');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get dashboard data',
        'workflow',
        error
      );
    }
  }

  // Optimization Operations

  async optimizeWorkflow(workflowId: string, optimization: any): Promise<any> {
    try {
      const response = await this.httpClient.post(`/api/workflows/${workflowId}/optimize`, optimization);
      
      // Publish optimization applied event
      await this.eventBus.publishWorkflowEvent(
        'OPTIMIZATION_SUGGESTED' as any,
        {
          workflow_id: workflowId,
          optimization_type: optimization.type,
          recommendations: optimization.recommendations,
          applied: response.data.applied
        }
      );

      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to optimize workflow',
        'workflow',
        error
      );
    }
  }

  async applyOptimization(workflowId: string, optimizationId: string): Promise<any> {
    try {
      const response = await this.httpClient.post(`/api/workflows/${workflowId}/optimizations/${optimizationId}/apply`);
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to apply optimization',
        'workflow',
        error
      );
    }
  }

  async getOptimizationHistory(workflowId: string): Promise<any> {
    try {
      const response = await this.httpClient.get(`/api/workflows/${workflowId}/optimizations`);
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get optimization history',
        'workflow',
        error
      );
    }
  }

  // Configuration Management

  async getConfiguration(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/config');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get configuration',
        'workflow',
        error
      );
    }
  }

  async updateConfiguration(config: any): Promise<any> {
    try {
      const response = await this.httpClient.post('/api/config', config);
      
      // Publish configuration synced event
      await this.eventBus.publishWorkflowEvent(
        'CONFIGURATION_SYNCED' as any,
        {
          configuration: config,
          timestamp: new Date()
        }
      );

      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to update configuration',
        'workflow',
        error
      );
    }
  }

  // Event Handling

  setupEventHandlers(): void {
    // Listen for evolution events that might trigger workflow responses
    this.eventBus.subscribeToSystemEvents('evolution', async (event) => {
      try {
        await this.handleEvolutionEvent(event);
      } catch (error) {
        this.logger.error('Error handling evolution event:', error);
      }
    });
  }

  private async handleEvolutionEvent(event: any): void {
    switch (event.type) {
      case 'MUTATION_APPLIED':
        // Adjust workflow parameters based on mutation
        await this.adjustWorkflowsForMutation(event.payload);
        break;
      
      case 'FITNESS_CALCULATED':
        // Update agent performance targets based on fitness
        await this.updateAgentTargetsFromFitness(event.payload);
        break;
      
      case 'SYSTEM_EVOLVED':
        // Reconfigure workflows for evolved system
        await this.reconfigureForEvolution(event.payload);
        break;
      
      case 'HEALING_COMPLETED':
        // Resume workflows after healing
        await this.resumeWorkflowsAfterHealing(event.payload);
        break;
    }
  }

  private async adjustWorkflowsForMutation(mutationData: any): Promise<void> {
    // TODO: Implement workflow adjustment based on mutations
    this.logger.debug('Adjusting workflows for mutation:', mutationData.mutation_type);
  }

  private async updateAgentTargetsFromFitness(fitnessData: any): Promise<void> {
    // TODO: Implement agent target updates based on fitness
    this.logger.debug('Updating agent targets from fitness:', fitnessData.overall_score);
  }

  private async reconfigureForEvolution(evolutionData: any): Promise<void> {
    // TODO: Implement workflow reconfiguration for system evolution
    this.logger.debug('Reconfiguring workflows for evolution:', evolutionData.generation);
  }

  private async resumeWorkflowsAfterHealing(healingData: any): Promise<void> {
    // TODO: Implement workflow resumption after healing
    this.logger.debug('Resuming workflows after healing:', healingData.strategy_used);
  }

  // Utility Methods

  async testConnection(): Promise<boolean> {
    try {
      await this.getHealth();
      return true;
    } catch (error) {
      return false;
    }
  }

  getConnectionInfo(): any {
    return {
      baseUrl: this.baseUrl,
      hasApiKey: !!unifiedConfig.workflow.apiKey,
      timeout: this.httpClient.defaults.timeout
    };
  }
}