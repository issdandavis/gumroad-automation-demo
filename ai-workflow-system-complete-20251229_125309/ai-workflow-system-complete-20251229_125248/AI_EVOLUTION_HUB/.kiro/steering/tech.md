---
inclusion: always
---

# Technology Stack: AI Evolution Hub

## Primary Technologies

- **Backend**: Python 3.12, FastAPI, Pydantic for data validation
- **AI Framework**: Custom evolution engine with hypothesis for property-based testing
- **Database**: DynamoDB for evolution logs, S3 for snapshots and backups
- **Infrastructure**: AWS CDK, Lambda functions, API Gateway
- **Testing**: Pytest, Hypothesis (property-based), LocalStack for AWS mocking
- **Communication**: Multi-protocol support (HTTP, WebSocket, email routing)

## AWS Services

- **Compute**: Lambda functions for mutation processing, healing, and fitness monitoring
- **Storage**: DynamoDB (evolution logs), S3 (snapshots, backups), Secrets Manager (API keys)
- **Networking**: API Gateway (REST APIs), CloudFront (future dashboard), VPC (security)
- **AI/ML**: Bedrock (future AI provider integration), Comprehend (feedback analysis)
- **Monitoring**: CloudWatch (metrics, logs), X-Ray (tracing), CloudTrail (audit)

## MCP Servers Configured

- **awslabs.aws-api-mcp-server**: AWS service management and deployment
- **awslabs.aws-knowledge-mcp-server**: AWS documentation and best practices
- **awslabs.cdk-mcp-server**: CDK best practices and infrastructure patterns
- **awslabs.dynamodb-mcp-server**: Database operations and optimization
- **awslabs.cloudwatch-mcp-server**: Monitoring and alerting setup
- **awslabs.cloudtrail-mcp-server**: Audit logging and compliance
- **awslabs.aws-pricing-mcp-server**: Cost estimation and optimization
- **awslabs.bedrock-kb-retrieval-mcp-server**: AI feedback analysis (optional)

## Development Tools

- **IDE**: VS Code, Cursor with Python extensions
- **Version Control**: Git, GitHub with automated evolution tracking
- **CI/CD**: GitHub Actions with security scanning and cost checks
- **Package Management**: pip, poetry for dependency management
- **Testing**: pytest with hypothesis for property-based testing

## Technical Constraints

- All mutations must be reversible with automatic rollback capability
- Maximum 30-second response time for mutation risk assessment
- Support for offline operation with queue-based sync when connectivity restored
- Encryption at rest and in transit for all AI communication data
- Rate limiting to prevent mutation storms or feedback loops

## Architecture Decisions

- **Event-driven architecture**: Pub/sub pattern for loose coupling between components
- **Circuit breaker pattern**: Resilient external API calls with automatic fallback
- **Immutable snapshots**: All system states preserved for rollback capability
- **Risk-based autonomy**: Configurable thresholds for human vs automatic approval
- **Multi-platform sync**: Redundant storage across cloud providers for reliability