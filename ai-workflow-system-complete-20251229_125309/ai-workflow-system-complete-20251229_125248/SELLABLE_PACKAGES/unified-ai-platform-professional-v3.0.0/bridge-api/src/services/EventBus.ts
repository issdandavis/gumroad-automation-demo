/**
 * Cross-System Event Bus Service
 * Handles event communication between Evolution Framework and Workflow Orchestrator
 */

import Redis from 'redis';
import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { CrossSystemEvent, EventType, BridgeAPIError } from '../types';
import { unifiedConfig } from '../config';
import { Logger } from './Logger';

export class EventBusService extends EventEmitter {
  private redisClient: Redis.RedisClientType;
  private subscriberClient: Redis.RedisClientType;
  private isConnected: boolean = false;
  private eventQueue: CrossSystemEvent[] = [];
  private processingQueue: boolean = false;
  private logger: Logger;

  // Event channels
  private readonly EVOLUTION_CHANNEL = 'evolution:events';
  private readonly WORKFLOW_CHANNEL = 'workflow:events';
  private readonly BRIDGE_CHANNEL = 'bridge:events';
  private readonly SYSTEM_CHANNEL = 'system:events';

  constructor() {
    super();
    this.logger = new Logger('EventBusService');
    this.initializeRedis();
  }

  private async initializeRedis(): Promise<void> {
    try {
      const redisConfig = unifiedConfig.shared.redis;
      
      // Create Redis clients
      this.redisClient = Redis.createClient({
        socket: {
          host: redisConfig.host,
          port: redisConfig.port
        },
        password: redisConfig.password,
        database: redisConfig.db
      });

      this.subscriberClient = this.redisClient.duplicate();

      // Set up error handlers
      this.redisClient.on('error', (error) => {
        this.logger.error('Redis client error:', error);
        this.isConnected = false;
      });

      this.subscriberClient.on('error', (error) => {
        this.logger.error('Redis subscriber error:', error);
      });

      // Connect clients
      await this.redisClient.connect();
      await this.subscriberClient.connect();

      this.isConnected = true;
      this.logger.info('Redis clients connected successfully');

      // Set up subscriptions
      await this.setupSubscriptions();
      
      // Process any queued events
      this.processEventQueue();

    } catch (error) {
      this.logger.warn('Redis not available, running in memory-only mode:', error.message);
      this.isConnected = false;
      
      // Continue without Redis for development
      // Events will be handled in-memory only
      this.logger.info('Event bus initialized in memory-only mode');
    }
  }

  private async setupSubscriptions(): Promise<void> {
    try {
      // Subscribe to all event channels
      await this.subscriberClient.subscribe(this.EVOLUTION_CHANNEL, (message) => {
        this.handleIncomingEvent(message, 'evolution');
      });

      await this.subscriberClient.subscribe(this.WORKFLOW_CHANNEL, (message) => {
        this.handleIncomingEvent(message, 'workflow');
      });

      await this.subscriberClient.subscribe(this.SYSTEM_CHANNEL, (message) => {
        this.handleIncomingEvent(message, 'system');
      });

      this.logger.info('Event subscriptions established');
    } catch (error) {
      this.logger.error('Failed to setup subscriptions:', error);
      throw error;
    }
  }

  private handleIncomingEvent(message: string, source: string): void {
    try {
      const event: CrossSystemEvent = JSON.parse(message);
      
      // Validate event structure
      if (!this.validateEvent(event)) {
        this.logger.warn('Invalid event received:', event);
        return;
      }

      // Add metadata
      event.timestamp = new Date(event.timestamp);
      
      this.logger.debug(`Received event from ${source}:`, event.type);
      
      // Emit to local listeners
      this.emit('event', event);
      this.emit(event.type, event);
      
      // Route to appropriate handlers
      this.routeEvent(event);

    } catch (error) {
      this.logger.error('Error handling incoming event:', error);
    }
  }

  private validateEvent(event: any): event is CrossSystemEvent {
    return (
      event &&
      typeof event.id === 'string' &&
      typeof event.type === 'string' &&
      typeof event.source === 'string' &&
      typeof event.target === 'string' &&
      event.payload !== undefined &&
      event.timestamp
    );
  }

  private routeEvent(event: CrossSystemEvent): void {
    // Route events based on target
    switch (event.target) {
      case 'evolution':
        this.routeToEvolution(event);
        break;
      case 'workflow':
        this.routeToWorkflow(event);
        break;
      case 'both':
        this.routeToEvolution(event);
        this.routeToWorkflow(event);
        break;
    }

    // Handle cross-system optimizations
    if (this.isCrossSystemOptimizationEvent(event)) {
      this.handleOptimizationEvent(event);
    }
  }

  private routeToEvolution(event: CrossSystemEvent): void {
    // Emit events that the evolution system should handle
    this.emit('evolution:event', event);
  }

  private routeToWorkflow(event: CrossSystemEvent): void {
    // Emit events that the workflow system should handle
    this.emit('workflow:event', event);
  }

  private isCrossSystemOptimizationEvent(event: CrossSystemEvent): boolean {
    return [
      EventType.PERFORMANCE_THRESHOLD,
      EventType.OPTIMIZATION_SUGGESTED,
      EventType.SYSTEM_HEALING
    ].includes(event.type);
  }

  private handleOptimizationEvent(event: CrossSystemEvent): void {
    this.emit('optimization:event', event);
  }

  // Public API methods

  /**
   * Publish an event to the event bus
   */
  async publishEvent(event: Omit<CrossSystemEvent, 'id' | 'timestamp'>): Promise<void> {
    const fullEvent: CrossSystemEvent = {
      ...event,
      id: uuidv4(),
      timestamp: new Date()
    };

    if (!this.isConnected) {
      this.logger.debug('Redis not connected, handling event in-memory:', fullEvent.type);
      
      // Handle event locally without Redis
      this.handleIncomingEvent(JSON.stringify(fullEvent), fullEvent.source);
      return;
    }

    try {
      const channel = this.getChannelForSource(fullEvent.source);
      await this.redisClient.publish(channel, JSON.stringify(fullEvent));
      
      this.logger.debug(`Published event to ${channel}:`, fullEvent.type);
      
      // Emit locally as well
      this.emit('published', fullEvent);
      
    } catch (error) {
      this.logger.error('Failed to publish event:', error);
      
      // Fallback to in-memory handling
      this.handleIncomingEvent(JSON.stringify(fullEvent), fullEvent.source);
    }
  }

  /**
   * Publish evolution system event
   */
  async publishEvolutionEvent(
    type: EventType,
    payload: any,
    target: 'workflow' | 'both' = 'workflow',
    correlationId?: string
  ): Promise<void> {
    await this.publishEvent({
      type,
      source: 'evolution',
      target,
      payload,
      correlationId,
      priority: this.getEventPriority(type)
    });
  }

  /**
   * Publish workflow system event
   */
  async publishWorkflowEvent(
    type: EventType,
    payload: any,
    target: 'evolution' | 'both' = 'evolution',
    correlationId?: string
  ): Promise<void> {
    await this.publishEvent({
      type,
      source: 'workflow',
      target,
      payload,
      correlationId,
      priority: this.getEventPriority(type)
    });
  }

  /**
   * Subscribe to specific event types
   */
  subscribeToEvents(eventTypes: EventType[], callback: (event: CrossSystemEvent) => void): void {
    eventTypes.forEach(eventType => {
      this.on(eventType, callback);
    });
  }

  /**
   * Subscribe to events from specific system
   */
  subscribeToSystemEvents(
    system: 'evolution' | 'workflow',
    callback: (event: CrossSystemEvent) => void
  ): void {
    this.on(`${system}:event`, callback);
  }

  /**
   * Subscribe to optimization events
   */
  subscribeToOptimizationEvents(callback: (event: CrossSystemEvent) => void): void {
    this.on('optimization:event', callback);
  }

  /**
   * Get event statistics
   */
  getEventStats(): {
    queuedEvents: number;
    isConnected: boolean;
    totalPublished: number;
    totalReceived: number;
  } {
    return {
      queuedEvents: this.eventQueue.length,
      isConnected: this.isConnected,
      totalPublished: this.listenerCount('published'),
      totalReceived: this.listenerCount('event')
    };
  }

  // Helper methods

  private getChannelForSource(source: string): string {
    switch (source) {
      case 'evolution':
        return this.EVOLUTION_CHANNEL;
      case 'workflow':
        return this.WORKFLOW_CHANNEL;
      default:
        return this.BRIDGE_CHANNEL;
    }
  }

  private getEventPriority(type: EventType): 'low' | 'medium' | 'high' | 'critical' {
    const criticalEvents = [EventType.SYSTEM_HEALING, EventType.SYSTEM_STOPPED];
    const highEvents = [EventType.PERFORMANCE_THRESHOLD, EventType.MUTATION_APPLIED];
    const mediumEvents = [EventType.WORKFLOW_COMPLETED, EventType.AGENT_CONFIGURED];
    
    if (criticalEvents.includes(type)) return 'critical';
    if (highEvents.includes(type)) return 'high';
    if (mediumEvents.includes(type)) return 'medium';
    return 'low';
  }

  private async processEventQueue(): Promise<void> {
    if (this.processingQueue || !this.isConnected || this.eventQueue.length === 0) {
      return;
    }

    this.processingQueue = true;
    
    try {
      while (this.eventQueue.length > 0 && this.isConnected) {
        const event = this.eventQueue.shift()!;
        await this.publishEvent(event);
        
        // Small delay to prevent overwhelming Redis
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    } catch (error) {
      this.logger.error('Error processing event queue:', error);
    } finally {
      this.processingQueue = false;
    }
  }

  /**
   * Graceful shutdown
   */
  async shutdown(): Promise<void> {
    try {
      this.logger.info('Shutting down event bus...');
      
      // Process remaining queued events
      if (this.eventQueue.length > 0) {
        this.logger.info(`Processing ${this.eventQueue.length} queued events before shutdown`);
        await this.processEventQueue();
      }

      // Close Redis connections
      if (this.redisClient?.isOpen) {
        await this.redisClient.quit();
      }
      
      if (this.subscriberClient?.isOpen) {
        await this.subscriberClient.quit();
      }

      this.isConnected = false;
      this.logger.info('Event bus shutdown complete');
      
    } catch (error) {
      this.logger.error('Error during event bus shutdown:', error);
    }
  }
}

// Singleton instance
export const eventBus = new EventBusService();