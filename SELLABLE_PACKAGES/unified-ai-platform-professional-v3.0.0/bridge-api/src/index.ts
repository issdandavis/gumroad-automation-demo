/**
 * Unified AI Platform Bridge API
 * Main entry point for the integration service
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { v4 as uuidv4 } from 'uuid';

import { unifiedConfig } from './config';
import { Logger } from './services/Logger';
import { EventBusService, eventBus } from './services/EventBus';
import { SystemIntegrationService } from './services/SystemIntegration';
import { 
  ApiResponse, 
  BridgeAPIError, 
  WebSocketMessage,
  EventType 
} from './types';

// Initialize services
const logger = new Logger('BridgeAPI');
const systemIntegration = new SystemIntegrationService(eventBus);

// Create Express app
const app = express();
const server = createServer(app);

// WebSocket server for real-time updates
const wss = new WebSocketServer({ server });

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors(unifiedConfig.bridge.cors));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
  const requestId = uuidv4();
  req.requestId = requestId;
  
  logger.info(`${req.method} ${req.path}`, {
    requestId,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  
  next();
});

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const status = await systemIntegration.getUnifiedStatus();
    
    res.json({
      success: true,
      data: status,
      timestamp: new Date(),
      requestId: req.requestId
    });
  } catch (error) {
    logger.error('Health check failed:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'HEALTH_CHECK_FAILED',
        message: 'Health check failed'
      },
      timestamp: new Date(),
      requestId: req.requestId
    });
  }
});

// Unified system status endpoint
app.get('/api/status', async (req, res) => {
  try {
    const status = await systemIntegration.getUnifiedStatus();
    
    const response: ApiResponse = {
      success: true,
      data: status,
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.json(response);
  } catch (error) {
    logger.error('Failed to get system status:', error);
    
    const response: ApiResponse = {
      success: false,
      error: {
        code: 'STATUS_ERROR',
        message: 'Failed to retrieve system status'
      },
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.status(500).json(response);
  }
});

// Evolution system endpoints
app.post('/api/evolution/mutate', async (req, res) => {
  try {
    const result = await systemIntegration.proposeMutation(req.body);
    
    const response: ApiResponse = {
      success: true,
      data: result,
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.json(response);
  } catch (error) {
    logger.error('Mutation proposal failed:', error);
    
    const response: ApiResponse = {
      success: false,
      error: {
        code: 'MUTATION_ERROR',
        message: error.message
      },
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.status(500).json(response);
  }
});

app.get('/api/evolution/fitness', async (req, res) => {
  try {
    const fitness = await systemIntegration.getEvolutionFitness();
    
    const response: ApiResponse = {
      success: true,
      data: fitness,
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.json(response);
  } catch (error) {
    logger.error('Failed to get fitness data:', error);
    
    const response: ApiResponse = {
      success: false,
      error: {
        code: 'FITNESS_ERROR',
        message: error.message
      },
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.status(500).json(response);
  }
});

// Workflow system endpoints
app.post('/api/workflow/execute', async (req, res) => {
  try {
    const result = await systemIntegration.executeWorkflow(req.body);
    
    const response: ApiResponse = {
      success: true,
      data: result,
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.json(response);
  } catch (error) {
    logger.error('Workflow execution failed:', error);
    
    const response: ApiResponse = {
      success: false,
      error: {
        code: 'WORKFLOW_ERROR',
        message: error.message
      },
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.status(500).json(response);
  }
});

app.post('/api/workflow/agents', async (req, res) => {
  try {
    const result = await systemIntegration.configureAgent(req.body);
    
    const response: ApiResponse = {
      success: true,
      data: result,
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.json(response);
  } catch (error) {
    logger.error('Agent configuration failed:', error);
    
    const response: ApiResponse = {
      success: false,
      error: {
        code: 'AGENT_CONFIG_ERROR',
        message: error.message
      },
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.status(500).json(response);
  }
});

// Cross-system optimization endpoints
app.post('/api/optimize/workflow/:workflowId', async (req, res) => {
  try {
    const { workflowId } = req.params;
    const result = await systemIntegration.optimizeWorkflowWithEvolution(workflowId);
    
    const response: ApiResponse = {
      success: true,
      data: result,
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.json(response);
  } catch (error) {
    logger.error('Workflow optimization failed:', error);
    
    const response: ApiResponse = {
      success: false,
      error: {
        code: 'OPTIMIZATION_ERROR',
        message: error.message
      },
      timestamp: new Date(),
      requestId: req.requestId
    };
    
    res.status(500).json(response);
  }
});

// Event streaming endpoint
app.get('/api/events/stream', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'
  });

  const sendEvent = (event: any) => {
    res.write(`data: ${JSON.stringify(event)}\n\n`);
  };

  // Subscribe to all events
  const eventHandler = (event: any) => {
    sendEvent({
      type: 'event',
      payload: event,
      timestamp: new Date()
    });
  };

  eventBus.on('event', eventHandler);

  // Send initial connection event
  sendEvent({
    type: 'connected',
    payload: { message: 'Event stream connected' },
    timestamp: new Date()
  });

  // Cleanup on disconnect
  req.on('close', () => {
    eventBus.off('event', eventHandler);
  });
});

// WebSocket handling for real-time updates
wss.on('connection', (ws, req) => {
  const clientId = uuidv4();
  logger.info(`WebSocket client connected: ${clientId}`);

  // Send welcome message
  const welcomeMessage: WebSocketMessage = {
    type: 'status',
    payload: { message: 'Connected to Unified AI Platform Bridge' },
    timestamp: new Date(),
    id: uuidv4()
  };
  
  ws.send(JSON.stringify(welcomeMessage));

  // Subscribe to events
  const eventHandler = (event: any) => {
    const message: WebSocketMessage = {
      type: 'event',
      payload: event,
      timestamp: new Date(),
      id: uuidv4()
    };
    
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify(message));
    }
  };

  eventBus.on('event', eventHandler);

  // Handle incoming messages
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      logger.debug(`WebSocket message from ${clientId}:`, message);
      
      // Handle different message types
      switch (message.type) {
        case 'subscribe':
          // Handle event subscriptions
          break;
        case 'ping':
          ws.send(JSON.stringify({ type: 'pong', timestamp: new Date() }));
          break;
      }
    } catch (error) {
      logger.error(`WebSocket message error from ${clientId}:`, error);
    }
  });

  // Cleanup on disconnect
  ws.on('close', () => {
    logger.info(`WebSocket client disconnected: ${clientId}`);
    eventBus.off('event', eventHandler);
  });

  ws.on('error', (error) => {
    logger.error(`WebSocket error for ${clientId}:`, error);
  });
});

// Error handling middleware
app.use((error: Error, req: any, res: any, next: any) => {
  logger.error('Unhandled error:', error);
  
  const response: ApiResponse = {
    success: false,
    error: {
      code: error instanceof BridgeAPIError ? error.code : 'INTERNAL_ERROR',
      message: error.message
    },
    timestamp: new Date(),
    requestId: req.requestId
  };
  
  const statusCode = error instanceof BridgeAPIError ? error.statusCode : 500;
  res.status(statusCode).json(response);
});

// 404 handler
app.use((req, res) => {
  const response: ApiResponse = {
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: `Endpoint ${req.method} ${req.path} not found`
    },
    timestamp: new Date(),
    requestId: req.requestId
  };
  
  res.status(404).json(response);
});

// Graceful shutdown handling
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

async function gracefulShutdown(signal: string) {
  logger.info(`Received ${signal}, starting graceful shutdown...`);
  
  try {
    // Close WebSocket server
    wss.close();
    
    // Close HTTP server
    server.close();
    
    // Shutdown services
    await eventBus.shutdown();
    systemIntegration.shutdown();
    
    logger.info('Graceful shutdown complete');
    process.exit(0);
  } catch (error) {
    logger.error('Error during shutdown:', error);
    process.exit(1);
  }
}

// Start server
const port = unifiedConfig.bridge.port;

server.listen(port, () => {
  logger.info(`🌉 Bridge API server started on port ${port}`);
  logger.info(`📊 Health check: http://localhost:${port}/health`);
  logger.info(`🔄 Event stream: http://localhost:${port}/api/events/stream`);
  logger.info(`🔌 WebSocket: ws://localhost:${port}`);
  
  // Publish system started event
  eventBus.publishEvent({
    type: EventType.SYSTEM_STARTED,
    source: 'evolution',
    target: 'both',
    payload: {
      service: 'bridge-api',
      version: '1.0.0',
      port,
      timestamp: new Date()
    }
  });
});

// Extend Express Request type
declare global {
  namespace Express {
    interface Request {
      requestId: string;
    }
  }
}

export { app, server, eventBus, systemIntegration };