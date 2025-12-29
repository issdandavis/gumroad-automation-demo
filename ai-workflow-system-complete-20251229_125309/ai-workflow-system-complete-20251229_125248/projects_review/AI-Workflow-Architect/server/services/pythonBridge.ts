/**
 * Python Bridge Service
 * 
 * Interfaces between Express.js backend and Python self-evolving AI framework.
 * Handles communication, data transformation, and error handling.
 */

import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';
import axios from 'axios';
import WebSocket from 'ws';

interface PythonFrameworkConfig {
  pythonPath: string;
  frameworkPath: string;
  apiPort: number;
  websocketPort: number;
}

interface SystemDNA {
  version: string;
  birth_timestamp: string;
  generation: number;
  fitness_score: number;
  core_traits: {
    communication_channels: number;
    language_support: number;
    ai_participants: string[];
    evolutionary_features: string[];
    autonomy_level: number;
  };
  mutations: MutationRecord[];
}

interface MutationRecord {
  id: string;
  timestamp: string;
  type: string;
  description: string;
  fitness_impact: number;
  risk_score: number;
  auto_approved: boolean;
  source_ai?: string;
}

interface FitnessScore {
  overall: number;
  success_rate: number;
  healing_speed: number;
  cost_efficiency: number;
  uptime: number;
  timestamp: string;
  trend: 'improving' | 'stable' | 'declining';
}

interface MutationProposal {
  type: string;
  description: string;
  fitness_impact: number;
  source_ai?: string;
}

interface EvolutionStatus {
  running: boolean;
  initialized: boolean;
  version: string;
  dna: SystemDNA;
  fitness: FitnessScore;
  pending_approvals: number;
  recent_mutations: MutationRecord[];
}

export class PythonBridge extends EventEmitter {
  private config: PythonFrameworkConfig;
  private pythonProcess: ChildProcess | null = null;
  private apiClient: axios.AxiosInstance;
  private websocket: WebSocket | null = null;
  private isInitialized = false;

  constructor(config: PythonFrameworkConfig) {
    super();
    this.config = config;
    
    // Setup API client for HTTP communication
    this.apiClient = axios.create({
      baseURL: `http://localhost:${config.apiPort}`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Setup error handling
    this.apiClient.interceptors.response.use(
      response => response,
      error => {
        console.error('Python API Error:', error.message);
        this.emit('error', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Initialize the Python framework
   */
  async initialize(): Promise<boolean> {
    try {
      console.log('🐍 Starting Python self-evolving AI framework...');
      
      // Start Python process
      await this.startPythonProcess();
      
      // Wait for API to be ready
      await this.waitForAPI();
      
      // Setup WebSocket connection
      await this.