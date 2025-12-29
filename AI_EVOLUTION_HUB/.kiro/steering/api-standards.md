---
inclusion: fileMatch
fileMatchPattern: "**/{api,routes,endpoints,controllers}/**/*.py"
---

# API Standards: AI Evolution Hub

## REST Conventions

- Resource nouns: `/mutations`, `/fitness`, `/snapshots`
- Methods: GET (read), POST (create), PUT (update), DELETE (delete)
- Status: 200 (success), 201 (created), 202 (accepted), 400 (client error), 500 (server error)
- Async operations: Return 202 with operation ID for polling

## Response Format

```python
# Success
{
    "data": {},
    "meta": {
        "timestamp": "2025-01-01T00:00:00Z",
        "request_id": "uuid",
        "generation": 42
    }
}

# Error
{
    "error": {
        "code": "MUTATION_VALIDATION_FAILED",
        "message": "Mutation exceeds risk threshold",
        "details": {
            "risk_score": 0.85,
            "threshold": 0.7
        }
    },
    "meta": {...}
}
```

## Authentication

- API Key authentication for AI systems
- JWT tokens for human administrators
- Rate limiting per API key (1000 requests/hour)
- Separate endpoints for autonomous vs supervised operations

## Validation

- Pydantic models for all request/response validation
- Risk score validation (0.0-1.0 range)
- Mutation type validation against enum
- Fitness score bounds checking

## Documentation

- OpenAPI 3.0 specs in api-specs/
- Use AWS Documentation MCP for AWS integration patterns
- Include examples for all mutation types and risk scenarios