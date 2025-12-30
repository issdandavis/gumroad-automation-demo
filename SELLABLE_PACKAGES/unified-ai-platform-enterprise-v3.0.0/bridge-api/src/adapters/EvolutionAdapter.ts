/**
 * Evolution Framework Adapter
 * Handles communication with the Self-Evolving AI Framework
 */

import axios, { AxiosInstance } from 'axios';
import { EventBusService } from '../services/EventBus';
import { Logger } from '../services/Logger';
import { unifiedConfig } from '../config';
import { IntegrationError } from '../types';

export class EvolutionAdapter {
  private httpClient: AxiosInstance;
  private eventBus: EventBusService;
  private logger: Logger;
  private baseUrl: string;

  constructor(eventBus: EventBusService) {
    this.eventBus = eventBus;
    this.logger = new Logger('EvolutionAdapter');
    this.baseUrl = unifiedConfig.evolution.apiUrl;

    this.httpClient = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        ...(unifiedConfig.evolution.apiKey && {
          'Authorization': `Bearer ${unifiedConfig.evolution.apiKey}`
        })
      }
    });

    // Set up request/response interceptors
    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.httpClient.interceptors.request.use(
      (config) => {
        this.logger.debug(`Evolution API request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        this.logger.error('Evolution API request error:', error);
        return Promise.reject(error);
      }
    );

    this.httpClient.interceptors.response.use(
      (response) => {
        this.logger.debug(`Evolution API response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        this.logger.error('Evolution API response error:', error.response?.status, error.message);
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
      this.logger.warn('Evolution Framework not reachable:', error.message);
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
        'Evolution Framework health check failed',
        'evolution',
        error
      );
    }
  }

  // Mutation Operations

  async proposeMutation(mutation: any): Promise<any> {
    try {
      const response = await this.httpClient.post('/api/mutate', mutation);
      
      // If mutation was applied, publish event
      if (response.data.approved) {
        await this.eventBus.publishEvolutionEvent(
          'MUTATION_APPLIED' as any,
          {
            mutation_id: response.data.result?.mutation_id,
            mutation_type: mutation.type,
            fitness_impact: mutation.fitness_impact,
            auto_approved: response.data.auto
          }
        );
      }

      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to propose mutation',
        'evolution',
        error
      );
    }
  }

  async getMutationHistory(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/mutations/history');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get mutation history',
        'evolution',
        error
      );
    }
  }

  // Fitness Operations

  async getFitness(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/fitness');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get fitness metrics',
        'evolution',
        error
      );
    }
  }

  async updateFitnessTargets(targets: Record<string, number>): Promise<any> {
    try {
      const response = await this.httpClient.post('/api/fitness/targets', { targets });
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to update fitness targets',
        'evolution',
        error
      );
    }
  }

  // Storage and Sync Operations

  async triggerSync(): Promise<any> {
    try {
      const response = await this.httpClient.post('/api/sync');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to trigger sync',
        'evolution',
        error
      );
    }
  }

  async getSyncStatus(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/sync/status');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get sync status',
        'evolution',
        error
      );
    }
  }

  // Rollback Operations

  async rollback(snapshotId: string): Promise<any> {
    try {
      const response = await this.httpClient.post('/api/rollback', { snapshot_id: snapshotId });
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to rollback system',
        'evolution',
        error
      );
    }
  }

  async getSnapshots(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/snapshots');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get snapshots',
        'evolution',
        error
      );
    }
  }

  // AI Provider Operations

  async getProviderStats(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/providers/stats');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get provider stats',
        'evolution',
        error
      );
    }
  }

  async configureProvider(providerId: string, config: any): Promise<any> {
    try {
      const response = await this.httpClient.post(`/api/providers/${providerId}/config`, config);
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to configure provider',
        'evolution',
        error
      );
    }
  }

  // Healing Operations

  async triggerHealing(errorType: string, context: any): Promise<any> {
    try {
      const response = await this.httpClient.post('/api/heal', {
        error_type: errorType,
        context
      });
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to trigger healing',
        'evolution',
        error
      );
    }
  }

  async getHealingStats(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/healing/stats');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get healing stats',
        'evolution',
        error
      );
    }
  }

  // Dashboard and Analytics

  async getDashboardData(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/dashboard');
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get dashboard data',
        'evolution',
        error
      );
    }
  }

  async getAnalytics(timeRange: string = '24h'): Promise<any> {
    try {
      const response = await this.httpClient.get(`/api/analytics?range=${timeRange}`);
      return response.data;
    } catch (error) {
      throw new IntegrationError(
        'Failed to get analytics',
        'evolution',
        error
      );
    }
  }

  // Event Handling

  setupEventHandlers(): void {
    // Listen for workflow events that might trigger evolution responses
    this.eventBus.subscribeToSystemEvents('workflow', async (event) => {
      try {
        await this.handleWorkflowEvent(event);
      } catch (error) {
        this.logger.error('Error handling workflow event:', error);
      }
    });
  }

  private async handleWorkflowEvent(event: any): void {
    switch (event.type) {
      case 'WORKFLOW_COMPLETED':
        // Analyze workflow performance and suggest mutations
        await this.analyzeWorkflowPerformance(event.payload);
        break;
      
      case 'AGENT_PERFORMANCE_UPDATED':
        // Update fitness targets based on agent performance
        await this.updateFitnessBasedOnAgentPerformance(event.payload);
        break;
      
      case 'PERFORMANCE_THRESHOLD':
        // Trigger healing if performance drops
        await this.handlePerformanceThreshold(event.payload);
        break;
    }
  }

  private async analyzeWorkflowPerformance(workflowData: any): Promise<void> {
    // TODO: Implement workflow performance analysis
    this.logger.debug('Analyzing workflow performance:', workflowData.workflow_id);
  }

  private async updateFitnessBasedOnAgentPerformance(agentData: any): Promise<void> {
    // TODO: Implement fitness target updates based on agent performance
    this.logger.debug('Updating fitness targets based on agent performance:', agentData.agent_id);
  }

  private async handlePerformanceThreshold(thresholdData: any): Promise<void> {
    // TODO: Implement performance threshold handling
    this.logger.debug('Handling performance threshold:', thresholdData);
  }
}