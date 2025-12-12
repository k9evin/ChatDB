# ChatDB - Production-Ready Agentic SQL Assistant

A production-grade SQL assistant built with **LangGraph** that enables non-technical users to query databases using natural language. The system uses multi-agent orchestration, RAG for semantic schema matching, and a multi-layer validation pipeline.

## 🚀 Features

- **Natural Language to SQL**: Convert plain English queries to SQL
- **Multi-Agent Orchestration**: LangGraph-based workflow with intelligent routing
- **RAG-Powered Schema Discovery**: Semantic search for relevant tables and columns
- **Multi-Layer Validation**: Syntax and schema validation before execution
- **Streaming Responses**: Real-time WebSocket streaming for better UX
- **Production-Ready**: Error handling, retry logic, and observability support

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ (Next.js + TypeScript)
│  (WebSocket)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FastAPI   │ (REST + WebSocket)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LangGraph  │ (Agent Orchestration)
└──────┬──────┘
       │
       ├──► Database Tools (Introspection)
       ├──► RAG (Schema Search)
       ├──► Validation (Syntax + Schema)
       └──► Execution (Query Runner)
```

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- OpenRouter API key (or OpenAI API key)

## 🛠️ Installation

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

5. **Configure environment variables:**
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   OPENROUTER_MODEL=openai/gpt-4o-mini
   DATABASE_URL=sqlite:///./demo_database.db
   ```

6. **Create sample database:**
   ```bash
   python -m backend.database.sample_data
   ```

7. **Start the backend server:**
   ```bash
   python -m backend.main
   # Or
   uvicorn backend.api.main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Update `config.ts` if needed:**
   ```typescript
   backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   ```
   http://localhost:3000
   ```

## 📁 Project Structure

```
chatdb/
├── backend/
│   ├── agent/              # LangGraph agent workflow
│   │   ├── graph.py        # Graph construction
│   │   ├── nodes.py        # Agent nodes
│   │   ├── routers.py      # Conditional routing
│   │   ├── state.py        # State schema
│   │   └── prompts.py      # System prompts
│   ├── tools/              # Agent tools
│   │   ├── database.py     # Database introspection
│   │   ├── rag.py          # RAG for schema search
│   │   ├── validation.py   # SQL validation
│   │   └── execution.py    # Query execution
│   ├── database/           # Database management
│   │   ├── connection.py  # Connection manager
│   │   └── sample_data.py  # Sample database
│   ├── api/                # FastAPI endpoints
│   │   └── main.py         # WebSocket + REST API
│   └── config/             # Configuration
│       └── settings.py     # Settings management
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── hooks/              # Custom hooks
│   └── contexts/           # React contexts
└── README.md
```

## 🔧 Configuration

### Environment Variables

**Backend (`.env`):**
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_MODEL`: Model to use (default: `openai/gpt-4o-mini`)
- `DATABASE_URL`: Database connection string
- `LANGCHAIN_TRACING_V2`: Enable LangSmith tracing (optional)
- `LANGCHAIN_API_KEY`: LangSmith API key (optional)

**Frontend (`config.ts`):**
- `NEXT_PUBLIC_BACKEND_URL`: Backend API URL (default: `http://localhost:8000`)

## 🎯 Usage

### Basic Query

1. Start the backend and frontend servers
2. Open the web interface
3. Type a natural language query:
   ```
   Show me all customers from the last month
   ```
4. The agent will:
   - Search for relevant tables
   - Get table schemas
   - Generate SQL
   - Validate the query
   - Execute and return results

### Example Queries

- "Show me all orders with amount greater than 100"
- "List customers who have placed more than 3 orders"
- "What's the total revenue by product category?"
- "Find the top 5 customers by order amount"

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Manual Testing

1. **Test WebSocket connection:**
   ```bash
   # Use a WebSocket client or the frontend
   ```

2. **Test REST API:**
   ```bash
   curl -X POST http://localhost:8000/api/query \
     -H "Content-Type: application/json" \
     -d '{"message": "show me all customers"}'
   ```

## 🔍 Observability

### LangSmith Integration

Enable LangSmith tracing for debugging and monitoring:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=ChatDB-Agent
```

## 🚨 Error Handling

The system includes:
- **Syntax Validation**: Prevents SQL injection and dangerous operations
- **Schema Validation**: Ensures column names exist
- **Retry Logic**: Maximum 3 retries per query
- **Error Messages**: Clear, actionable error messages

## 🔐 Security

- **Read-Only Queries**: Only SELECT queries are allowed
- **Input Validation**: Multi-layer validation pipeline
- **SQL Injection Protection**: Parameterized queries and validation
- **CORS Configuration**: Configurable CORS settings

## 📚 API Documentation

### WebSocket Endpoint

**URL:** `ws://localhost:8000/ws/chat`

**Protocol:**
```json
// Client → Server
{"message": "show me all customers"}

// Server → Client (streaming)
{"type": "token", "content": "I'll"}
{"type": "token", "content": " help"}
{"type": "tool_start", "tool": "search_relevant_tables"}
{"type": "tool_result", "tool": "search_relevant_tables", "output": {...}}
{"type": "complete", "content": "Here are the results..."}
```

### REST Endpoint

**POST** `/api/query`

```json
{
  "message": "show me all customers",
  "thread_id": "optional_thread_id"
}
```

**Response:**
```json
{
  "response": "Here are all customers...",
  "conversation_id": "thread_abc123",
  "messages": [...]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [OpenRouter](https://openrouter.ai/)
- Frontend built with [Next.js](https://nextjs.org/)

## 🐛 Troubleshooting

### Backend won't start
- Check that Python 3.11+ is installed
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check `.env` file exists and has valid API keys

### WebSocket connection fails
- Ensure backend is running on the correct port
- Check CORS settings in `backend/config/settings.py`
- Verify WebSocket URL in frontend `config.ts`

### Database connection errors
- Verify `DATABASE_URL` in `.env`
- For SQLite, ensure the database file path is correct
- For PostgreSQL/MySQL, verify credentials and network access

## 📞 Support

For issues and questions, please open an issue on GitHub.
