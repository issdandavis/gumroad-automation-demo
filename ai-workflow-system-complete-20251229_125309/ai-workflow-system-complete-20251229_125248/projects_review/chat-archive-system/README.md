# Chat Archive System

🚀 AI-powered chat archive and knowledge base system with auto-categorization, tagging, and expansion features

## Overview

This full-stack application automatically archives, organizes, and expands chat messages from multiple sources (Slack, direct imports) using AI-powered categorization. It provides a searchable knowledge base with intelligent tagging, notion integration, and systematic content expansion.

## Features

### Core Functionality
- **Multi-Source Import**: Slack integration, manual CSV upload, API endpoints
- **AI-Powered Categorization**: Automatic topic detection and tagging using OpenAI/Langchain
- **Smart Search**: Full-text search with filters (date, source, tags, project)
- **Auto-Expansion**: AI generates detailed summaries and related content
- **Notion Sync**: Bi-directional sync with Notion databases

### Organization
- **Dynamic Tagging**: Auto-tags for World Building, AI Automation, Technical Projects, Store/Business
- **Project Linking**: Associate chats with specific projects or initiatives
- **Timeline View**: Chronological organization with context preservation

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: OpenAI API, Langchain
- **Task Queue**: Celery with Redis
- **Testing**: Pytest, pytest-asyncio

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **State Management**: React Query + Context API
- **UI Library**: TailwindCSS + shadcn/ui
- **Forms**: React Hook Form + Zod

### Integrations
- Slack SDK (message import)
- Notion API (database sync)
- OpenAI API (categorization, expansion)

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

## Project Structure

```
chat-archive-system/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Config, security, database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── ai/           # AI categorization
│   │   │   ├── integrations/ # Slack, Notion
│   │   │   └── storage/      # Database operations
│   │   └── tasks/            # Celery tasks
│   ├── alembic/              # Database migrations
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # Utilities
│   │   └── types/            # TypeScript types
│   ├── public/
│   └── package.json
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- OpenAI API key
- Slack Bot Token (optional)
- Notion API key (optional)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone https://github.com/issdandavis/chat-archive-system.git
cd chat-archive-system
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatarchive

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your_openai_key

# Slack (Optional)
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your_secret

# Notion (Optional)
NOTION_API_KEY=your_notion_key
NOTION_DATABASE_ID=your_database_id

# JWT Authentication
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Endpoints

### Chat Messages
- `POST /api/chats/` - Create new chat entry
- `GET /api/chats/` - List all chats (with filters)
- `GET /api/chats/{id}` - Get specific chat
- `PUT /api/chats/{id}` - Update chat
- `DELETE /api/chats/{id}` - Delete chat

### Integrations
- `POST /api/integrations/slack/import` - Import from Slack
- `POST /api/integrations/notion/sync` - Sync with Notion

### AI Operations
- `POST /api/ai/categorize/{chat_id}` - Categorize single chat
- `POST /api/ai/expand/{chat_id}` - Generate expanded content
- `POST /api/ai/batch-categorize` - Categorize multiple chats

## Usage Examples

### Import Slack Messages
```python
import requests

response = requests.post(
    "http://localhost:8000/api/integrations/slack/import",
    json={
        "channel_id": "C01234567",
        "start_date": "2025-01-01",
        "end_date": "2025-01-31"
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

### Search Chats
```javascript
const searchChats = async (query) => {
  const response = await fetch(
    `http://localhost:8000/api/chats/?search=${query}&tags=AI Automation`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return response.json();
};
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Docker Production Build
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configurations
- Development: `docker-compose.yml`
- Production: `docker-compose.prod.yml`

## Roadmap

- [ ] GitHub Copilot generates initial project structure
- [ ] FastAPI backend with PostgreSQL setup
- [ ] React frontend with TailwindCSS
- [ ] Slack integration for message import
- [ ] OpenAI-powered categorization
- [ ] Notion API bi-directional sync
- [ ] Advanced search and filtering
- [ ] Batch AI operations
- [ ] Export functionality (CSV, JSON, Markdown)
- [ ] Custom tag management
- [ ] Analytics dashboard

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/issdandavis/chat-archive-system/issues
- Documentation: [Wiki](https://github.com/issdandavis/chat-archive-system/wiki)

## Acknowledgments

- OpenAI for GPT API
- Slack for API access
- Notion for database integration
- FastAPI and React communities
