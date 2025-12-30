/**
 * System Integration Service
 * Handles communication with Evolution Framework and Workflow Orchestrator
 */

import { EventBusService } from './EventBus';
import { Logger } from './Logger';
import { EvolutionAdapter } from '../adapters/EvolutionAdapter';
import { WorkflowAdapter } from '../adapters/WorkflowAdapter';
import { 
  UnifiedSystemStatus, 
  HealthCheck, 
  IntegrationError,
  EventType 
} from '../types';
import { unifiedConfig } from '../config';

export class SystemIntegrationService {
  private evolutionAdapter: EvolutionAdapter;
  private workflowAdapter: WorkflowAdapter;
  private eventBus: EventBusService;
  private logger: Logger;
  private healthCheckInterval: NodeJS.Timeout | null = null;

  constructor(eventBus: EventBusService) {
    this.eventBus = eventBus;
    this.logger = new Logger('SystemIntegration');
    
    // Initialize adapters
    this.evolutionAdapter = new EvolutionAdapter(eventBus);
    this.workflowAdapter = new WorkflowAdapter(eventBus);

    this.startHealthChecks();
  }

  // Evolution Framework Integration

  async getEvolutionStatus(): Promise<any> {
    try {
      return await this.evolutionAdapter.getStatus();
    } catch (error) {
      this.logger.warn('Failed to get evolution status:', error);
      return null;
    }
  }

  async proposeMutation(mutation: any): Promise<any> {
    try {
      return await this.evolutionAdapter.proposeMutation(mutation);
    } catch (error) {
      throw new IntegrationError(
        'Failed to propose mutation',
        'evolution',
        error
      );
    }
  }

  async getEvolutionFitness(): Promise<any> {
    try {
      return await this.evolutionAdapter.getFitness();
    } catch (error) {
      throw new IntegrationError(
        'Failed to get fitness metrics',
        'evolution',
        error
      );
    }
  }

  async triggerEvolutionSync(): Promise<any> {
    try {
      return await this.evolutionAdapter.triggerSync();
    } catch (error) {
      throw new IntegrationError(
        'Failed to trigger evolution sync',
        'evolution',
        error
      );
    }
  }

  // Workflow Orchestrator Integration

  async getWorkflowStatus(): Promise<any> {
    try {
      return await this.workflowAdapter.getStatus();
    } catch (error) {
      this.logger.warn('Failed to get workflow status:', error);
      return null;
    }
  }

  async executeWorkflow(workflow: any): Promise<any> {
    try {
      return await this.workflowAdapter.executeWorkflow(workflow);
    } catch (error) {
      throw new IntegrationError(
        'Failed to execute workflow',
        'workflow',
        error
      );
    }
  }

  async configureAgent(agentConfig: any): Promise<any> {
    try {
      return await this.workflowAdapter.configureAgent(agentConfig);
    } catch (error) {
      throw new IntegrationError(
        'Failed to configure agent',
        'workflow',
        error
      );
    }
  }

  async getWorkflowMetrics(): Promise<any> {
    try {
      return await this.workflowAdapter.getMetrics();
    } catch (error) {
      throw new IntegrationError(
        'Failed to get workflow metrics',
        'workflow',
        error
      );
    }
  }

  // Unified System Status

  async getUnifiedStatus(): Promise<UnifiedSystemStatus> {
    const startTime = Date.now();
    
    try {
      // Get status from both systems in parallel
      const [evolutionStatus, workflowStatus] = await Promise.allSettled([
        this.getEvolutionStatus(),
        this.getWorkflowStatus()
      ]);

      const status: UnifiedSystemStatus = {
        bridge: {
          version: '1.0.0',
          uptime: process.uptime(),
          status: 'healthy',
          lastHealthCheck: new Date()
        },
        evolution: {
          connected: evolutionStatus.status === 'fulfilled' && evolutionStatus.value !== null && evolutionStatus.value.connected,
          ...(evolutionStatus.status === 'fulfilled' && evolutionStatus.value && evolutionStatus.value.connected && {
            version: evolutionStatus.value.version,
            generation: evolutionStatus.value.dna?.generation,
            fitnessScore: evolutionStatus.value.dna?.fitness_score,
            status: evolutionStatus.value.running ? 'running' : 'stopped'
          })
        },
        workflow: {
          connected: workflowStatus.status === 'fulfilled' && workflowStatus.value !== null && workflowStatus.value.connected,
          ...(workflowStatus.status === 'fulfilled' && workflowStatus.value && workflowStatus.value.connected && {
            version: workflowStatus.value.version,
            activeAgents: workflowStatus.value.agents?.active || 0,
            runningWorkflows: workflowStatus.value.workflows?.running || 0,
            status: workflowStatus.value.running ? 'running' : 'stopped'
          })
        },
        integration: {
          eventsSynced: this.eventBus.getEventStats().totalPublished,
          lastSyncTime: new Date(),
          configurationSynced: true,
          crossSystemOptimizations: 0 // TODO: Implement optimization tracking
        }
      };

      // Determine overall bridge status
      if (!status.evolution.connected && !status.workflow.connected) {
        status.bridge.status = 'unhealthy';
      } else if (!status.evolution.connected || !status.workflow.connected) {
        status.bridge.status = 'degraded';
      }

      return status;
      
    } catch (error) {
      this.logger.error('Failed to get unified status:', error);
      
      return {
        bridge: {
          version: '1.0.0',
          uptime: process.uptime(),
          status: 'unhealthy',
          lastHealthCheck: new Date()
        },
        evolution: {
          connected: false
        },
        workflow: {
          connected: false
        },
        integration: {
          eventsSynced: 0,
          lastSyncTime: new Date(),
          configurationSynced: false,
          crossSystemOptimizations: 0
        }
      };
    }
  }

  // Health Checks

  private startHealthChecks(): void {
    const interval = unifiedConfig.evolution.healthCheckInterval;
    
    this.healthCheckInterval = setInterval(async () => {
      await this.performHealthChecks();
    }, interval);

    this.logger.info(`Health checks started with ${interval}ms interval`);
  }

  private async performHealthChecks(): Promise<void> {
    try {
      const [evolutionHealth, workflowHealth] = await Promise.allSettled([
        this.checkEvolutionHealth(),
        this.checkWorkflowHealth()
      ]);

      // Publish health check events
      await this.eventBus.publishEvent({
        type: EventType.HEALTH_CHECK,
        source: 'evolution',
        target: 'both',
        payload: {
          evolution: evolutionHealth.status === 'fulfilled' ? evolutionHealth.value : null,
          workflow: workflowHealth.status === 'fulfilled' ? workflowHealth.value : null,
          timestamp: new Date()
        }
      });

    } catch (error) {
      this.logger.error('Health check failed:', error);
    }
  }

  private async checkEvolutionHealth(): Promise<HealthCheck> {
    const startTime = Date.now();
    
    try {
      const status = await this.evolutionAdapter.getStatus();
      
      return {
        service: 'evolution',
        status: status.connected ? 'healthy' : 'unhealthy',
        timestamp: new Date(),
        responseTime: Date.now() - startTime,
        details: status.connected ? undefined : { error: status.error }
      };
    } catch (error) {
      return {
        service: 'evolution',
        status: 'unhealthy',
        timestamp: new Date(),
        responseTime: Date.now() - startTime,
        details: { error: error.message }
      };
    }
  }

  private async checkWorkflowHealth(): Promise<HealthCheck> {
    const startTime = Date.now();
    
    try {
      const status = await this.workflowAdapter.getStatus();
      
      return {
        service: 'workflow',
        status: status.connected ? 'healthy' : 'unhealthy',
        timestamp: new Date(),
        responseTime: Date.now() - startTime,
        details: status.connected ? undefined : { error: status.error }
      };
    } catch (error) {
      return {
        service: 'workflow',
        status: 'unhealthy',
        timestamp: new Date(),
        responseTime: Date.now() - startTime,
        details: { error: error.message }
      };
    }
  }

  // Cross-System Operations

  async optimizeWorkflowWithEvolution(workflowId: string): Promise<any> {
    try {
      // Get workflow metrics
      const workflowMetrics = await this.getWorkflowMetrics();
      
      // Get evolution fitness data
      const evolutionFitness = await this.getEvolutionFitness();
      
      // Analyze and propose optimizations
      const optimization = {
        workflowId,
        currentMetrics: workflowMetrics,
        fitnessData: evolutionFitness,
        recommendations: this.generateOptimizationRecommendations(workflowMetrics, evolutionFitness)
      };

      // Use workflow adapter to apply optimizations
      const result = await this.workflowAdapter.optimizeWorkflow(workflowId, optimization);

      // Publish optimization event
      await this.eventBus.publishEvent({
        type: EventType.OPTIMIZATION_SUGGESTED,
        source: 'evolution',
        target: 'workflow',
        payload: { ...optimization, result }
      });

      return { ...optimization, result };
      
    } catch (error) {
      throw new IntegrationError(
        'Failed to optimize workflow with evolution',
        'evolution',
        error
      );
    }
  }

  private generateOptimizationRecommendations(workflowMetrics: any, fitnessData: any): any[] {
    // TODO: Implement intelligent optimization recommendation logic
    return [
      {
        type: 'parameter_adjustment',
        description: 'Adjust agent temperature based on performance data',
        confidence: 0.8,
        expectedImpact: 0.15
      }
    ];
  }

  // Cleanup

  shutdown(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
    
    this.logger.info('System integration service shutdown complete');
  }
}