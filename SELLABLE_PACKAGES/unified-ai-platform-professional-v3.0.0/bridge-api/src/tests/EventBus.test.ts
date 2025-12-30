/**
 * Property-based tests for EventBus service
 * Validates cross-system event delivery guarantees
 */

import { EventBusService } from '../services/EventBus';
import { EventType, CrossSystemEvent } from '../types';

// Mock Redis for testing
jest.mock('redis', () => ({
  createClient: jest.fn(() => ({
    connect: jest.fn().mockResolvedValue(undefined),
    duplicate: jest.fn(() => ({
      connect: jest.fn().mockResolvedValue(undefined),
      subscribe: jest.fn().mockResolvedValue(undefined),
      on: jest.fn()
    })),
    publish: jest.fn().mockResolvedValue(1),
    quit: jest.fn().mockResolvedValue(undefined),
    isOpen: true,
    on: jest.fn()
  }))
}));

describe('EventBus Service', () => {
  let eventBus: EventBusService;

  beforeEach(() => {
    eventBus = new EventBusService();
  });

  afterEach(async () => {
    await eventBus.shutdown();
  });

  describe('Property Tests', () => {
    /**
     * Property 1: Event Synchronization Consistency
     * For any cross-system event published by one system, 
     * the event should be delivered to the target system within 
     * the configured timeout period and processed exactly once.
     */
    test('Property: Event delivery consistency', async () => {
      // Property-based test data generation
      const testEvents: Omit<CrossSystemEvent, 'id' | 'timestamp'>[] = [
        {
          type: EventType.MUTATION_APPLIED,
          source: 'evolution',
          target: 'workflow',
          payload: { mutationId: 'test-1', impact: 5.0 }
        },
        {
          type: EventType.WORKFLOW_COMPLETED,
          source: 'workflow', 
          target: 'evolution',
          payload: { workflowId: 'test-2', success: true }
        },
        {
          type: EventType.PERFORMANCE_THRESHOLD,
          source: 'evolution',
          target: 'both',
          payload: { metric: 'cpu', value: 85, threshold: 80 }
        }
      ];

      const deliveredEvents: CrossSystemEvent[] = [];
      
      // Subscribe to events
      eventBus.on('event', (event: CrossSystemEvent) => {
        deliveredEvents.push(event);
      });

      // Publish all test events
      for (const eventData of testEvents) {
        await eventBus.publishEvent(eventData);
      }

      // Wait for event processing
      await new Promise(resolve => setTimeout(resolve, 100));

      // Verify all events were delivered exactly once
      expect(deliveredEvents).toHaveLength(testEvents.length);
      
      // Verify event structure and content
      deliveredEvents.forEach((deliveredEvent, index) => {
        const originalEvent = testEvents[index];
        
        expect(deliveredEvent.type).toBe(originalEvent.type);
        expect(deliveredEvent.source).toBe(originalEvent.source);
        expect(deliveredEvent.target).toBe(originalEvent.target);
        expect(deliveredEvent.payload).toEqual(originalEvent.payload);
        expect(deliveredEvent.id).toBeDefined();
        expect(deliveredEvent.timestamp).toBeInstanceOf(Date);
      });
    });

    /**
     * Property 2: Event ordering preservation
     * For any sequence of related events, they should be processed 
     * in the correct order to maintain system consistency.
     */
    test('Property: Event ordering preservation', async () => {
      const orderedEvents: Omit<CrossSystemEvent, 'id' | 'timestamp'>[] = [
        {
          type: EventType.WORKFLOW_STARTED,
          source: 'workflow',
          target: 'evolution',
          payload: { workflowId: 'test-workflow', step: 1 },
          correlationId: 'test-correlation'
        },
        {
          type: EventType.AGENT_CONFIGURED,
          source: 'workflow',
          target: 'evolution', 
          payload: { workflowId: 'test-workflow', step: 2 },
          correlationId: 'test-correlation'
        },
        {
          type: EventType.WORKFLOW_COMPLETED,
          source: 'workflow',
          target: 'evolution',
          payload: { workflowId: 'test-workflow', step: 3 },
          correlationId: 'test-correlation'
        }
      ];

      const receivedEvents: CrossSystemEvent[] = [];
      
      eventBus.on('event', (event: CrossSystemEvent) => {
        if (event.correlationId === 'test-correlation') {
          receivedEvents.push(event);
        }
      });

      // Publish events in sequence
      for (const eventData of orderedEvents) {
        await eventBus.publishEvent(eventData);
        // Small delay to ensure ordering
        await new Promise(resolve => setTimeout(resolve, 10));
      }

      // Wait for processing
      await new Promise(resolve => setTimeout(resolve, 100));

      // Verify events were received in correct order
      expect(receivedEvents).toHaveLength(orderedEvents.length);
      
      receivedEvents.forEach((event, index) => {
        expect(event.payload.step).toBe(index + 1);
      });
    });

    /**
     * Property 3: Event routing correctness
     * For any event with a specific target, it should only be 
     * routed to the intended system(s).
     */
    test('Property: Event routing correctness', async () => {
      const evolutionEvents: CrossSystemEvent[] = [];
      const workflowEvents: CrossSystemEvent[] = [];
      const bothEvents: CrossSystemEvent[] = [];

      // Subscribe to system-specific events
      eventBus.on('evolution:event', (event: CrossSystemEvent) => {
        evolutionEvents.push(event);
      });

      eventBus.on('workflow:event', (event: CrossSystemEvent) => {
        workflowEvents.push(event);
      });

      eventBus.on('event', (event: CrossSystemEvent) => {
        if (event.target === 'both') {
          bothEvents.push(event);
        }
      });

      // Test events with different targets
      await eventBus.publishEvent({
        type: EventType.MUTATION_APPLIED,
        source: 'evolution',
        target: 'workflow',
        payload: { test: 'workflow-only' }
      });

      await eventBus.publishEvent({
        type: EventType.WORKFLOW_COMPLETED,
        source: 'workflow',
        target: 'evolution',
        payload: { test: 'evolution-only' }
      });

      await eventBus.publishEvent({
        type: EventType.SYSTEM_HEALING,
        source: 'evolution',
        target: 'both',
        payload: { test: 'both-systems' }
      });

      // Wait for processing
      await new Promise(resolve => setTimeout(resolve, 100));

      // Verify routing correctness
      expect(workflowEvents).toHaveLength(1);
      expect(workflowEvents[0].payload.test).toBe('workflow-only');

      expect(evolutionEvents).toHaveLength(1);
      expect(evolutionEvents[0].payload.test).toBe('evolution-only');

      expect(bothEvents).toHaveLength(1);
      expect(bothEvents[0].payload.test).toBe('both-systems');
    });
  });

  describe('Unit Tests', () => {
    test('should initialize event bus service', () => {
      expect(eventBus).toBeInstanceOf(EventBusService);
    });

    test('should handle invalid events gracefully', async () => {
      const invalidEvent = {
        // Missing required fields
        type: EventType.MUTATION_APPLIED,
        payload: { test: true }
      } as any;

      // Should not throw error
      await expect(eventBus.publishEvent(invalidEvent)).rejects.toThrow();
    });

    test('should provide event statistics', () => {
      const stats = eventBus.getEventStats();
      
      expect(stats).toHaveProperty('queuedEvents');
      expect(stats).toHaveProperty('isConnected');
      expect(stats).toHaveProperty('totalPublished');
      expect(stats).toHaveProperty('totalReceived');
    });

    test('should handle graceful shutdown', async () => {
      await expect(eventBus.shutdown()).resolves.not.toThrow();
    });
  });
});