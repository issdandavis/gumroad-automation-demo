# Technology Stack & Build System

## Primary Tech Stack

### Frontend
- **React 18** with TypeScript - UI framework with concurrent features
- **Vite** - Build tool with HMR and fast development
- **Tailwind CSS v4** - Utility-first styling framework
- **shadcn/ui** - Component library (New York style)
- **Wouter** - Lightweight client-side routing
- **TanStack Query** - Server state management & caching
- **Framer Motion** - Animation library

### Backend
- **Express.js** with TypeScript - HTTP server framework
- **PostgreSQL** - Primary database
- **Drizzle ORM** - Type-safe database queries and migrations
- **FastAPI** (Python projects) - High-performance API framework
- **Node.js** - Runtime environment

### Development Tools
- **TypeScript 5.6+** - Type safety across frontend and backend
- **ESBuild** - Fast bundling and transpilation
- **Drizzle Kit** - Database schema management
- **tsx** - TypeScript execution for development

### Python Stack (Automation Projects)
- **FastAPI** - Modern Python web framework
- **Skyvern** - Browser automation
- **Selenium/Playwright** - Web automation drivers
- **Pydantic** - Data validation
- **uvicorn** - ASGI server

## Common Commands

### Development
```bash
# Start development server
npm run dev              # Starts both client (port 5000) and server
npm run dev:client       # Client only on port 5000

# Python projects
uvicorn main:app --reload  # Start FastAPI server
python main.py            # Alternative startup
```

### Database Operations
```bash
npm run db:push          # Push schema changes to database
npm run db:studio        # Open Drizzle Studio for database management
```

### Build & Deploy
```bash
npm run build            # Build for production
npm run start            # Start production server
npm run check            # TypeScript type checking
```

### Testing
```bash
# Python projects
pytest tests/            # Run test suite
pytest --cov=automation tests/  # With coverage
```

## Configuration Files

### Essential Config Files
- `package.json` - Node.js dependencies and scripts
- `tsconfig.json` - TypeScript configuration with path aliases
- `vite.config.ts` - Vite build configuration
- `drizzle.config.ts` - Database configuration
- `requirements.txt` - Python dependencies

### Environment Setup
- `.env.example` - Template for environment variables
- `.env` - Local environment (never commit)
- Required variables: `DATABASE_URL`, `SESSION_SECRET`

## Architecture Patterns

### Monorepo Structure
- `client/` - React frontend
- `server/` - Express backend
- `shared/` - Shared TypeScript types and schemas
- Path aliases: `@/*` for client, `@shared/*` for shared code

### Security Standards
- **AES-256-GCM encryption** for credential storage
- **Session-based authentication** with PostgreSQL storage
- **Rate limiting** on all API endpoints
- **Helmet middleware** for security headers
- **bcrypt** for password hashing

### Database Patterns
- **Drizzle ORM** with type-safe queries
- **Migration-based** schema management
- **Relational design** with proper foreign keys
- **Audit logging** for all sensitive operations

## Development Workflow

1. **Local Development**: Use `npm run dev` for hot reloading
2. **Database Changes**: Update `shared/schema.ts`, then `npm run db:push`
3. **Type Safety**: Run `npm run check` before commits
4. **Production Build**: `npm run build` creates optimized bundle
5. **Deployment**: Built for Replit hosting with automatic deployments