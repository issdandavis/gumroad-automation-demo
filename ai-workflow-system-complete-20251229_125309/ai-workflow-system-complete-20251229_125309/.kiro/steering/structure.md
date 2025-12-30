# Project Organization & Folder Structure

## Repository Structure

This is a multi-project repository organized for AI-powered business automation tools:

```
/
├── .kiro/                          # Kiro IDE configuration
│   └── steering/                   # AI assistant guidance rules
├── projects_review/                # Active development projects
│   ├── AI-Workflow-Architect/      # Main orchestration platform
│   ├── AI-Workflow-Architect.01.01.02/  # Latest version
│   ├── chat-archive-system/        # Chat archival tools
│   ├── gumroad-automation-demo/     # Gumroad automation
│   ├── morewritings/               # Content generation tools
│   └── Shopify/                    # Shopify integration tools
├── business-apps/                  # Production-ready applications
├── gumroad-products/               # Products for sale
├── shared-resources/               # Common utilities and components
├── archive/                        # Deprecated or experimental code
└── stable/                         # Stable releases and binaries
```

## AI Workflow Architect Structure

The main project follows a monorepo pattern:

```
AI-Workflow-Architect/
├── client/                         # React frontend application
│   ├── src/
│   │   ├── components/             # Reusable UI components
│   │   │   ├── assistant/          # AI assistant interface
│   │   │   ├── dashboard/          # Main dashboard components
│   │   │   ├── diff/               # Code diff viewer
│   │   │   ├── editor/             # Monaco code editor
│   │   │   └── ui/                 # shadcn/ui component library
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── lib/                    # Utility functions
│   │   ├── pages/                  # Route components
│   │   └── main.tsx                # Application entry point
│   ├── public/                     # Static assets
│   └── index.html                  # HTML template
├── server/                         # Express.js backend
│   ├── middleware/                 # Express middleware
│   │   ├── costGovernor.ts         # Budget enforcement
│   │   └── rateLimiter.ts          # API rate limiting
│   ├── services/                   # Business logic services
│   │   ├── orchestrator.ts         # Multi-agent coordination
│   │   ├── providerAdapters.ts     # AI provider clients
│   │   ├── vault.ts                # Encrypted credential storage
│   │   └── [other services]        # Various integrations
│   ├── auth.ts                     # Authentication logic
│   ├── db.ts                       # Database connection
│   ├── routes.ts                   # API route definitions
│   └── index.ts                    # Server entry point
├── shared/                         # Shared TypeScript definitions
│   └── schema.ts                   # Drizzle ORM schema
├── docs/                           # Project documentation
└── [config files]                  # Build and deployment config
```

## File Naming Conventions

### Frontend Components
- **PascalCase** for React components: `AgentCard.tsx`, `CommandInput.tsx`
- **camelCase** for hooks: `useAssistant.ts`, `useAuth.ts`
- **kebab-case** for UI components: `alert-dialog.tsx`, `button.tsx`

### Backend Files
- **camelCase** for services: `githubClient.ts`, `orchestrator.ts`
- **PascalCase** for middleware: `CostGovernor.ts`, `RateLimiter.ts`
- **lowercase** for core files: `auth.ts`, `db.ts`, `routes.ts`

### Configuration Files
- Standard names: `package.json`, `tsconfig.json`, `vite.config.ts`
- Environment: `.env.example`, `.env` (local only)

## Import Path Conventions

### Path Aliases (TypeScript)
```typescript
// Client-side imports
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/useAuth"

// Shared imports
import { schema } from "@shared/schema"

// Server-side imports (relative paths)
import { orchestrator } from "./services/orchestrator"
```

### Import Organization
1. **External libraries** (React, Express, etc.)
2. **Internal utilities** (from `@/lib` or `./utils`)
3. **Components** (UI components)
4. **Types** (TypeScript interfaces)

## Database Schema Organization

Located in `shared/schema.ts` using Drizzle ORM:

```typescript
// Core entities
users, orgs, projects

// AI-specific tables
agentRuns, messages, decisionTraces

// Integration tables
integrations, apiKeys, memoryItems

// Audit and governance
auditLog, budgets, secretsRef
```

## Environment Configuration

### Development
- `.env.example` - Template with all required variables
- `.env` - Local development (gitignored)
- Environment variables loaded via `dotenv`

### Production
- Environment variables set in hosting platform
- Database URL from hosting provider
- API keys stored in encrypted vault, not environment

## Asset Organization

### Static Assets
- `client/public/` - Favicon, manifest, static images
- `attached_assets/` - Generated images and temporary files
- `client/public/icons/` - PWA icons in multiple sizes

### Generated Content
- `dist/` - Production build output (gitignored)
- `node_modules/` - Dependencies (gitignored)
- Build artifacts cleaned on each build

## Documentation Structure

### Project-Level Docs
- `README.md` - Quick start and overview
- `docs/PROJECT_DOCUMENTATION.md` - Comprehensive documentation
- `docs/FULL_FEATURE_LIST.md` - Feature specifications

### Code Documentation
- **JSDoc comments** for complex functions
- **TypeScript interfaces** for data structures
- **Inline comments** for business logic

## Version Control Patterns

### Branch Strategy
- `main` - Production-ready code
- Feature branches for development
- Version tags for releases

### Commit Conventions
- Clear, descriptive commit messages
- Atomic commits for single features
- Reference issues in commit messages

### Gitignore Patterns
- Environment files (`.env`)
- Build outputs (`dist/`, `build/`)
- Dependencies (`node_modules/`)
- IDE files (`.vscode/`, except shared settings)
- Temporary files (`*.tmp`, `*.log`)