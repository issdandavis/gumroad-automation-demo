# 🚀 Self-Evolving AI Framework - Complete API Documentation

**Version:** 2.0.0  
**Last Updated:** December 29, 2025  
**Base URL:** `https://api.evolving-ai.com/v1`  

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Core Evolution API](#core-evolution-api)
3. [AI Provider Integration](#ai-provider-integration)
4. [Cost Management](#cost-management)
5. [Security & Compliance](#security--compliance)
6. [Monitoring & Analytics](#monitoring--analytics)
7. [System Management](#system-management)
8. [WebSocket Events](#websocket-events)
9. [Error Handling](#error-handling)
10. [Rate Limits](#rate-limits)
11. [SDK Examples](#sdk-examples)

---

## 🔐 Authentication

All API requests require authentication using API keys or JWT tokens.

### API Key Authentication

```http
GET /api/v1/evolution/status
Authorization: Bearer your-api-key-here
Content-Type: application/json
```

### JWT Token Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### Refresh Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 🧬 Core Evolution API

### Start Evolution Process

Start an autonomous evolution cycle for the AI system.

```http
POST /api/v1/evolution/start
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "target_fitness": 0.95,
  "max_iterations": 100,
  "mutation_rate": 0.1,
  "safety_threshold": 0.8,
  "optimization_goals": ["performance", "cost", "accuracy"]
}
```

**Response:**
```json
{
  "evolution_id": "evo_1234567890abcdef",
  "status": "started",
  "initial_fitness": 0.82,
  "target_fitness": 0.95,
  "estimated_duration": "2-4 hours",
  "created_at": "2025-12-29T10:30:00Z"
}
```

### Get Evolution Status

```http
GET /api/v1/evolution/{evolution_id}/status
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "evolution_id": "evo_1234567890abcdef",
  "status": "running",
  "current_fitness": 0.87,
  "target_fitness": 0.95,
  "progress_percentage": 65,
  "iterations_completed": 45,
  "mutations_applied": 12,
  "mutations_rejected": 3,
  "safety_violations": 0,
  "estimated_completion": "2025-12-29T12:15:00Z",
  "last_updated": "2025-12-29T11:45:00Z"
}
```

### Stop Evolution Process

```http
POST /api/v1/evolution/{evolution_id}/stop
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "reason": "manual_stop",
  "save_progress": true
}
```

### Get Evolution History

```http
GET /api/v1/evolution/history
Authorization: Bearer your-api-key
```

**Query Parameters:**
- `limit` (integer): Number of results to return (default: 50, max: 200)
- `offset` (integer): Offset for pagination (default: 0)
- `status` (string): Filter by status (started, running, completed, failed, stopped)
- `start_date` (string): ISO 8601 date string
- `end_date` (string): ISO 8601 date string

**Response:**
```json
{
  "evolutions": [
    {
      "evolution_id": "evo_1234567890abcdef",
      "status": "completed",
      "initial_fitness": 0.82,
      "final_fitness": 0.94,
      "duration": "3h 24m",
      "mutations_applied": 18,
      "cost": 12.45,
      "created_at": "2025-12-29T08:00:00Z",
      "completed_at": "2025-12-29T11:24:00Z"
    }
  ],
  "total_count": 156,
  "has_more": true
}
```

### Rollback Evolution

```http
POST /api/v1/evolution/{evolution_id}/rollback
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "checkpoint_id": "checkpoint_abc123",
  "reason": "performance_degradation"
}
```

---

## 🤖 AI Provider Integration

### List Available Providers

```http
GET /api/v1/ai/providers
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "providers": [
    {
      "id": "openai",
      "name": "OpenAI",
      "status": "active",
      "models": ["gpt-4", "gpt-3.5-turbo"],
      "cost_per_1k_tokens": 0.002,
      "avg_response_time": 0.8,
      "reliability_score": 0.95,
      "last_health_check": "2025-12-29T11:50:00Z"
    },
    {
      "id": "anthropic",
      "name": "Anthropic",
      "status": "active",
      "models": ["claude-3-opus", "claude-3-sonnet"],
      "cost_per_1k_tokens": 0.003,
      "avg_response_time": 0.6,
      "reliability_score": 0.98,
      "last_health_check": "2025-12-29T11:50:00Z"
    },
    {
      "id": "bedrock",
      "name": "AWS Bedrock",
      "status": "active",
      "models": ["anthropic.claude-3-sonnet", "meta.llama2-70b"],
      "cost_per_1k_tokens": 0.0015,
      "avg_response_time": 1.2,
      "reliability_score": 0.92,
      "last_health_check": "2025-12-29T11:50:00Z"
    }
  ]
}
```

### Send AI Request with Auto-Routing

```http
POST /api/v1/ai/chat
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "Analyze this customer feedback and provide insights."
    }
  ],
  "routing_preference": "cost_optimized",
  "max_tokens": 1000,
  "temperature": 0.7,
  "auto_fallback": true
}
```

**Response:**
```json
{
  "id": "req_1234567890abcdef",
  "provider_used": "bedrock",
  "model": "anthropic.claude-3-sonnet",
  "response": {
    "role": "assistant",
    "content": "Based on the customer feedback analysis..."
  },
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 300,
    "total_tokens": 450
  },
  "cost": 0.675,
  "response_time": 1.1,
  "created_at": "2025-12-29T11:55:00Z"
}
```

### Configure Provider Preferences

```http
PUT /api/v1/ai/providers/preferences
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "primary_provider": "bedrock",
  "fallback_order": ["openai", "anthropic"],
  "routing_strategy": "cost_optimized",
  "cost_weight": 0.4,
  "performance_weight": 0.3,
  "reliability_weight": 0.3,
  "auto_failover": true,
  "max_retry_attempts": 3
}
```

---

## 💰 Cost Management

### Get Cost Summary

```http
GET /api/v1/costs/summary
Authorization: Bearer your-api-key
```

**Query Parameters:**
- `period` (string): time, day, week, month, year (default: month)
- `start_date` (string): ISO 8601 date string
- `end_date` (string): ISO 8601 date string

**Response:**
```json
{
  "period": "month",
  "total_cost": 245.67,
  "budget_limit": 1000.00,
  "budget_used_percentage": 24.57,
  "cost_by_provider": {
    "openai": 98.45,
    "anthropic": 76.32,
    "bedrock": 45.23,
    "xai": 25.67
  },
  "cost_by_operation": {
    "chat_completion": 156.78,
    "text_generation": 45.23,
    "evolution_cycles": 43.66
  },
  "daily_breakdown": [
    {
      "date": "2025-12-29",
      "cost": 12.45,
      "requests": 1250
    }
  ]
}
```

### Set Budget Limits

```http
PUT /api/v1/costs/budget
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "monthly_limit": 1000.00,
  "daily_limit": 50.00,
  "alert_thresholds": [0.5, 0.8, 0.9],
  "auto_throttle_at": 0.95,
  "emergency_stop_at": 1.0
}
```

### Get Cost Optimization Recommendations

```http
GET /api/v1/costs/recommendations
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "recommendations": [
    {
      "type": "provider_switch",
      "description": "Switch 30% of requests from OpenAI to Bedrock",
      "potential_savings": 45.67,
      "confidence": 0.85,
      "implementation_effort": "low"
    },
    {
      "type": "request_optimization",
      "description": "Reduce max_tokens for routine requests",
      "potential_savings": 23.45,
      "confidence": 0.92,
      "implementation_effort": "medium"
    }
  ],
  "total_potential_savings": 69.12
}
```

---

## 🔒 Security & Compliance

### Encrypt Sensitive Data

```http
POST /api/v1/security/encrypt
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "data": "sensitive information to encrypt",
  "encryption_type": "AES-256-GCM",
  "key_id": "key_12345"
}
```

**Response:**
```json
{
  "encrypted_data": "eyJhbGciOiJBMjU2R0NNIiwiZW5jIjoiQTI1NkdDTSJ9...",
  "key_id": "key_12345",
  "encryption_type": "AES-256-GCM",
  "created_at": "2025-12-29T12:00:00Z"
}
```

### Decrypt Data

```http
POST /api/v1/security/decrypt
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "encrypted_data": "eyJhbGciOiJBMjU2R0NNIiwiZW5jIjoiQTI1NkdDTSJ9...",
  "key_id": "key_12345"
}
```

### Get Audit Logs

```http
GET /api/v1/security/audit-logs
Authorization: Bearer your-api-key
```

**Query Parameters:**
- `event_type` (string): Filter by event type
- `user_id` (string): Filter by user ID
- `start_date` (string): ISO 8601 date string
- `end_date` (string): ISO 8601 date string
- `limit` (integer): Number of results (default: 100, max: 1000)

**Response:**
```json
{
  "audit_logs": [
    {
      "id": "log_1234567890abcdef",
      "event_type": "data_access",
      "user_id": "user_12345",
      "resource": "evolution_data",
      "action": "read",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2025-12-29T12:05:00Z",
      "metadata": {
        "evolution_id": "evo_1234567890abcdef"
      }
    }
  ],
  "total_count": 1567
}
```

### Compliance Report

```http
GET /api/v1/security/compliance-report
Authorization: Bearer your-api-key
```

**Query Parameters:**
- `framework` (string): GDPR, SOC2, HIPAA, ISO27001
- `format` (string): json, pdf (default: json)

**Response:**
```json
{
  "framework": "GDPR",
  "compliance_status": "compliant",
  "last_assessment": "2025-12-29T00:00:00Z",
  "requirements": [
    {
      "requirement": "Data Encryption",
      "status": "compliant",
      "evidence": "AES-256-GCM encryption implemented"
    },
    {
      "requirement": "Right to Deletion",
      "status": "compliant",
      "evidence": "Data deletion API implemented"
    }
  ],
  "recommendations": [
    "Regular security training for staff",
    "Quarterly penetration testing"
  ]
}
```

---

## 📊 Monitoring & Analytics

### Get System Health

```http
GET /api/v1/monitoring/health
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "status": "healthy",
  "uptime_percentage": 99.95,
  "response_time_p95": 85,
  "error_rate": 0.12,
  "active_alerts": 0,
  "system_metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.4,
    "network_throughput": 1250000
  },
  "evolution_metrics": {
    "active_processes": 3,
    "current_fitness": 0.89,
    "mutations_per_hour": 2.5
  },
  "last_updated": "2025-12-29T12:10:00Z"
}
```

### Get Performance Metrics

```http
GET /api/v1/monitoring/metrics
Authorization: Bearer your-api-key
```

**Query Parameters:**
- `metric_names` (string): Comma-separated list of metric names
- `start_time` (string): ISO 8601 timestamp
- `end_time` (string): ISO 8601 timestamp
- `granularity` (string): minute, hour, day (default: hour)

**Response:**
```json
{
  "metrics": {
    "response_time": {
      "data_points": [
        {
          "timestamp": "2025-12-29T12:00:00Z",
          "value": 85.5
        },
        {
          "timestamp": "2025-12-29T12:01:00Z",
          "value": 92.1
        }
      ],
      "unit": "milliseconds",
      "aggregation": "average"
    },
    "fitness_score": {
      "data_points": [
        {
          "timestamp": "2025-12-29T12:00:00Z",
          "value": 0.89
        }
      ],
      "unit": "score",
      "aggregation": "latest"
    }
  }
}
```

### Create Alert

```http
POST /api/v1/monitoring/alerts
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "name": "High Error Rate Alert",
  "description": "Triggers when error rate exceeds 5%",
  "condition": "error_rate > 5",
  "severity": "high",
  "notification_channels": ["email", "slack"],
  "enabled": true
}
```

### List Alerts

```http
GET /api/v1/monitoring/alerts
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_1234567890abcdef",
      "name": "High Error Rate Alert",
      "description": "Triggers when error rate exceeds 5%",
      "condition": "error_rate > 5",
      "severity": "high",
      "is_active": false,
      "triggered_at": null,
      "resolved_at": null,
      "notification_channels": ["email", "slack"],
      "enabled": true,
      "created_at": "2025-12-29T10:00:00Z"
    }
  ]
}
```

---

## ⚙️ System Management

### Get System Configuration

```http
GET /api/v1/system/config
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "evolution": {
    "default_fitness_threshold": 0.8,
    "default_mutation_rate": 0.1,
    "safety_checks_enabled": true,
    "max_concurrent_evolutions": 5
  },
  "ai_providers": {
    "default_provider": "bedrock",
    "auto_failover": true,
    "max_retry_attempts": 3
  },
  "security": {
    "encryption_enabled": true,
    "audit_logging": true,
    "session_timeout": 3600
  },
  "monitoring": {
    "metrics_retention_days": 90,
    "alert_check_interval": 60
  }
}
```

### Update System Configuration

```http
PUT /api/v1/system/config
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "evolution": {
    "default_fitness_threshold": 0.85,
    "max_concurrent_evolutions": 10
  },
  "security": {
    "session_timeout": 7200
  }
}
```

### System Backup

```http
POST /api/v1/system/backup
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "backup_type": "full",
  "include_evolution_history": true,
  "include_metrics": false,
  "encryption_enabled": true
}
```

**Response:**
```json
{
  "backup_id": "backup_1234567890abcdef",
  "status": "started",
  "estimated_completion": "2025-12-29T13:00:00Z",
  "backup_size_estimate": "2.5 GB"
}
```

### System Restore

```http
POST /api/v1/system/restore
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "backup_id": "backup_1234567890abcdef",
  "restore_options": {
    "evolution_data": true,
    "configuration": true,
    "user_data": false
  }
}
```

---

## 🔄 WebSocket Events

Connect to real-time events via WebSocket at `wss://api.evolving-ai.com/v1/ws`

### Authentication

Send authentication message after connection:

```json
{
  "type": "auth",
  "token": "your-jwt-token"
}
```

### Subscribe to Events

```json
{
  "type": "subscribe",
  "events": ["evolution.progress", "system.alerts", "metrics.update"]
}
```

### Event Types

#### Evolution Progress

```json
{
  "type": "evolution.progress",
  "evolution_id": "evo_1234567890abcdef",
  "data": {
    "current_fitness": 0.87,
    "progress_percentage": 65,
    "mutations_applied": 12,
    "timestamp": "2025-12-29T12:15:00Z"
  }
}
```

#### System Alert

```json
{
  "type": "system.alert",
  "alert_id": "alert_1234567890abcdef",
  "data": {
    "name": "High Error Rate",
    "severity": "high",
    "status": "triggered",
    "timestamp": "2025-12-29T12:16:00Z"
  }
}
```

#### Metrics Update

```json
{
  "type": "metrics.update",
  "data": {
    "response_time": 95.2,
    "error_rate": 0.8,
    "fitness_score": 0.89,
    "timestamp": "2025-12-29T12:17:00Z"
  }
}
```

---

## ❌ Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid",
    "details": "Missing required field: target_fitness",
    "request_id": "req_1234567890abcdef",
    "timestamp": "2025-12-29T12:20:00Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |
| `EVOLUTION_FAILED` | 422 | Evolution process failed |
| `PROVIDER_ERROR` | 502 | AI provider error |
| `BUDGET_EXCEEDED` | 402 | Cost budget exceeded |

---

## 🚦 Rate Limits

### Default Limits

| Endpoint Category | Requests per Minute | Burst Limit |
|-------------------|---------------------|-------------|
| Authentication | 10 | 20 |
| Evolution Management | 60 | 100 |
| AI Requests | 1000 | 2000 |
| Monitoring | 300 | 500 |
| System Management | 30 | 50 |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640781600
X-RateLimit-Retry-After: 60
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "details": "Too many requests. Limit: 1000/minute",
    "retry_after": 60
  }
}
```

---

## 🛠️ SDK Examples

### Python SDK

```python
from evolving_ai import EvolutionClient

# Initialize client
client = EvolutionClient(api_key="your-api-key")

# Start evolution
evolution = await client.evolution.start(
    target_fitness=0.95,
    optimization_goals=["performance", "cost"]
)

# Monitor progress
async for update in client.evolution.stream_progress(evolution.id):
    print(f"Fitness: {update.current_fitness}")
    if update.status == "completed":
        break

# Send AI request with auto-routing
response = await client.ai.chat(
    messages=[{"role": "user", "content": "Hello!"}],
    routing_preference="cost_optimized"
)
```

### JavaScript SDK

```javascript
import { EvolutionClient } from '@evolving-ai/sdk';

// Initialize client
const client = new EvolutionClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.evolving-ai.com/v1'
});

// Start evolution
const evolution = await client.evolution.start({
  targetFitness: 0.95,
  optimizationGoals: ['performance', 'cost']
});

// Monitor via WebSocket
client.on('evolution.progress', (data) => {
  console.log(`Fitness: ${data.current_fitness}`);
});

// Send AI request
const response = await client.ai.chat({
  messages: [{ role: 'user', content: 'Hello!' }],
  routingPreference: 'cost_optimized'
});
```

### cURL Examples

#### Start Evolution

```bash
curl -X POST https://api.evolving-ai.com/v1/evolution/start \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "target_fitness": 0.95,
    "max_iterations": 100,
    "optimization_goals": ["performance", "cost"]
  }'
```

#### Send AI Request

```bash
curl -X POST https://api.evolving-ai.com/v1/ai/chat \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Analyze this data"}
    ],
    "routing_preference": "cost_optimized",
    "max_tokens": 1000
  }'
```

#### Get System Health

```bash
curl -X GET https://api.evolving-ai.com/v1/monitoring/health \
  -H "Authorization: Bearer your-api-key"
```

---

## 📚 Additional Resources

### OpenAPI Specification

Download the complete OpenAPI 3.0 specification:
- [JSON Format](https://api.evolving-ai.com/v1/openapi.json)
- [YAML Format](https://api.evolving-ai.com/v1/openapi.yaml)

### Postman Collection

Import our Postman collection for easy API testing:
- [Download Collection](https://api.evolving-ai.com/v1/postman-collection.json)

### Interactive API Explorer

Try the API interactively:
- [API Explorer](https://api.evolving-ai.com/docs)

### Support

- **Documentation:** [https://docs.evolving-ai.com](https://docs.evolving-ai.com)
- **Support Email:** support@evolving-ai.com
- **Discord Community:** [Join here](https://discord.gg/evolving-ai)
- **GitHub Issues:** [Report bugs](https://github.com/evolving-ai/framework/issues)

---

**🚀 Ready to build with the Self-Evolving AI Framework? Start with our [Quick Start Guide](https://docs.evolving-ai.com/quickstart) or explore the [SDK Documentation](https://docs.evolving-ai.com/sdk).**

*Last updated: December 29, 2025 | Version 2.0.0*