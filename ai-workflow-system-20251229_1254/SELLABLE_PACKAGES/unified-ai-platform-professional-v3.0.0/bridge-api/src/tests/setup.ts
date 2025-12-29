/**
 * Jest test setup
 */

// Mock Redis for tests
jest.mock('redis', () => ({
  createClient: jest.fn(() => ({
    connect: jest.fn().mockResolvedValue(undefined),
    quit: jest.fn().mockResolvedValue(undefined),
    publish: jest.fn().mockResolvedValue(1),
    subscribe: jest.fn().mockResolvedValue(undefined),
    on: jest.fn(),
    duplicate: jest.fn().mockReturnThis(),
    isOpen: true
  }))
}));

// Mock WebSocket
jest.mock('ws', () => ({
  WebSocketServer: jest.fn(() => ({
    on: jest.fn(),
    close: jest.fn()
  }))
}));

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.REDIS_HOST = 'localhost';
process.env.REDIS_PORT = '6379';
process.env.BRIDGE_PORT = '3001';
process.env.EVOLUTION_API_URL = 'http://localhost:5000';
process.env.WORKFLOW_API_URL = 'http://localhost:3000';