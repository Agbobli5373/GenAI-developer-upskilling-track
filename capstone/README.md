# Clause Intelligence System

An AI-powered legal document analysis platform that helps legal professionals analyze, manage, and update contractual agreements using advanced LLM capabilities, semantic search, and agentic AI.

## Tech Stack

- **Backend**: Python FastAPI with async/await patterns
- **Database**: Supabase (PostgreSQL with pgvector for embeddings)
- **Frontend**: React TypeScript with Vite
- **LLM**: Google Gemini 1.5 Pro/Flash
- **Document Processing**: PDF.js, python-docx, pytesseract
- **Vector Search**: Supabase pgvector extension
- **Authentication**: Supabase Auth with RLS

## Project Structure

```
clause-intelligence/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Docker configuration
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── App.tsx         # Main App component
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── database/               # Database migrations and schemas
│   └── migrations/         # SQL migration files
├── docs/                   # Documentation
└── docker-compose.yml      # Docker compose for development
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Supabase CLI

### Development Setup

1. **Clone the repository and navigate to the project directory**

2. **Set up the backend:**

   ```bash
   cd backend
   python -m venv venv

   # On Windows Git Bash/MINGW64:
   source venv/Scripts/activate

   # On Windows Command Prompt:
   # venv\Scripts\activate.bat

   # On Windows PowerShell:
   # venv\Scripts\Activate.ps1

   # On Linux/Mac:
   # source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Set up the frontend:**

   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables:**

   - Copy `.env.example` to `.env` in both backend and frontend directories
   - Update the configuration with your Supabase credentials

5. **Start the development servers:**

   ```bash
   # Backend (from backend directory)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Frontend (from frontend directory)
   npm run dev
   ```

## Week 1 Progress

- [x] Project structure initialization
- [ ] FastAPI backend setup with proper structure
- [ ] React TypeScript frontend with Vite setup
- [ ] Supabase project configuration
- [ ] Database schema design
- [ ] Authentication system implementation
- [ ] Development environment and CI/CD pipeline

## License

This project is licensed under the MIT License - see the LICENSE file for details.
