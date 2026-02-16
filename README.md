# Legal AI Assistant — MVP

AI-powered legal document analysis with citation-grounded responses. Upload legal documents (PDF, DOCX), ask questions, and get answers with citations back to source documents.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

## Quick Start

### 1. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- **`ANTHROPIC_API_KEY`** — for Claude chat responses ([get one here](https://console.anthropic.com/))
- **`OPENAI_API_KEY`** — for document embeddings ([get one here](https://platform.openai.com/api-keys))

### 2. Start PostgreSQL + pgvector

```bash
docker compose up -d
```

### 3. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

## Usage

1. Click **+ New Conversation** in the sidebar
2. **Upload a PDF or DOCX** using the upload area in the sidebar
3. **Ask a question** about your uploaded document in the chat
4. The assistant will respond with **cited answers** — click citations to see source text

## Architecture

- **Frontend**: Next.js 14 + Tailwind CSS
- **Backend**: FastAPI (Python) with async SQLAlchemy
- **Database**: PostgreSQL + pgvector for vector similarity search
- **LLM**: Claude (Anthropic) for chat responses
- **Embeddings**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Doc Parsing**: PyMuPDF (PDF) + python-docx (DOCX)
- **Retrieval**: Hybrid search (vector similarity + PostgreSQL full-text search) with reciprocal rank fusion

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents` | Upload a document |
| GET | `/api/documents` | List all documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| POST | `/api/conversations` | Create a conversation |
| GET | `/api/conversations` | List conversations |
| GET | `/api/conversations/{id}` | Get conversation with messages |
| DELETE | `/api/conversations/{id}` | Delete a conversation |
| POST | `/api/chat` | Send a message (SSE streaming) |
| GET | `/api/health` | Health check |

## Deploy to Render

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Deploy via Render Blueprint

1. Go to [Render Dashboard](https://dashboard.render.com/) → **Blueprints** → **New Blueprint Instance**
2. Connect your GitHub repo
3. Render will detect `render.yaml` and configure all three services automatically
4. Set the secret env vars when prompted:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
5. Click **Apply** — Render provisions PostgreSQL → backend → frontend

### 3. Enable pgvector

Render's PostgreSQL instances include pgvector. The app's `init_db()` creates the extension automatically (`CREATE EXTENSION IF NOT EXISTS vector`).

### 4. Update FRONTEND_URL

After the first deploy, update the backend's `FRONTEND_URL` env var in the Render dashboard to match your actual frontend URL (e.g., `https://legal-ai-frontend.onrender.com`).

### Notes

- **Uploads** persist on a Render Disk mounted at `/var/data/uploads`
- **Database URL** is injected automatically from the Render-managed PostgreSQL instance
- The `render.yaml` uses `starter` plans — upgrade as needed for production traffic

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```
