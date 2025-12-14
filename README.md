# 🏃 RunCoach AI

An AI-powered running coach that provides personalized training advice, nutrition guidance, and weather-aware workout recommendations using RAG (Retrieval-Augmented Generation) and AWS Bedrock.

![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonaws)
![LangChain](https://img.shields.io/badge/LangChain-1.1-green)

## Features

- 💬 **Conversational AI Coach** - Natural language chat interface for running advice
- 📚 **Knowledge Base (RAG)** - Answers grounded in running/nutrition PDFs via ChromaDB
- 🌤️ **Weather Integration** - Automatic weather checks for workout recommendations
- 🍎 **Nutrition Calculator** - BMR, TDEE, and macro calculations based on user profile
- ⏱️ **Pace Analysis** - Race time predictions and pacing strategies
- 👤 **User Profiles** - Personalized advice based on experience, goals, and metrics

## Architecture

```
┌─────────────────┐     HTTP/JSON      ┌──────────────────────────────────────┐
│   React + Vite  │ ◄────────────────► │            FastAPI Backend           │
│   (port 5173)   │                    │            (port 8000)               │
└─────────────────┘                    └──────────────────────────────────────┘
                                                        │
                                       ┌────────────────┼────────────────┐
                                       ▼                ▼                ▼
                               ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                               │  RAG Pipeline │ │   LLM Agent  │ │    Tools     │
                               │  (ChromaDB)   │ │  (Bedrock)   │ │  weather/    │
                               │              │ │              │ │  nutrition/  │
                               │  Titan       │ │  Nova Lite   │ │  pace        │
                               │  Embeddings  │ │              │ │              │
                               └──────────────┘ └──────────────┘ └──────────────┘
                                       │
                                       ▼
                               ┌──────────────┐
                               │     PDFs     │
                               │ (knowledge   │
                               │    base)     │
                               └──────────────┘
```

### Data Flow

1. **User sends message** → React frontend sends to `/api/chat` with user profile
2. **RAG search** → Agent automatically queries ChromaDB for relevant context
3. **LLM processing** → AWS Bedrock Nova Lite generates response with tool calls if needed
4. **Tool execution** → Weather, nutrition, or pace tools provide real-time data
5. **Response** → `<thinking>` tags parsed by frontend for collapsible reasoning display

## Prerequisites

- Python 3.10+
- Node.js 18+
- AWS Account with Bedrock access (Nova Lite + Titan Embeddings enabled)

## Setup

### 1. Clone and Install Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

```bash
cp sample.env .env
```

Edit `.env` with your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

### 3. Add Knowledge Base PDFs

Place running/nutrition PDF documents in:

```
backend/knowledge_base/pdfs/
```

The vector database will be created automatically on first startup.

### 4. Install Frontend

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload --port 8000
```

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## Project Structure

```
running-assistant/
├── backend/
│   ├── app.py              # FastAPI endpoints & Pydantic models
│   ├── agent.py            # LangChain agent with tool orchestration
│   ├── rag.py              # RAG pipeline (ChromaDB + embeddings)
│   ├── tools.py            # LangChain tools (weather, nutrition, pace)
│   ├── config.py           # AWS Bedrock client singleton
│   ├── requirements.txt
│   ├── sample.env
│   └── knowledge_base/
│       ├── pdfs/           # Drop PDFs here for RAG
│       └── chroma_db/      # Persisted vector store
│
├── frontend/
│   └── src/
│       ├── App.jsx                 # Main layout
│       ├── components/
│       │   ├── ChatContainer.jsx   # Message list
│       │   ├── ChatInput.jsx       # Input field
│       │   ├── ChatMessage.jsx     # Message bubble + thinking parser
│       │   ├── ProfileForm.jsx     # User profile sidebar
│       │   └── QuickQuestions.jsx  # Preset question buttons
│       ├── context/
│       │   └── UserContext.jsx     # Profile state management
│       └── services/
│           └── api.js              # Axios API client
│
└── README.md
```

## API Endpoints

| Method | Endpoint       | Description                               |
| ------ | -------------- | ----------------------------------------- |
| GET    | `/`            | Health check                              |
| POST   | `/api/chat`    | Send message (with optional user_profile) |
| GET    | `/api/profile` | Get current profile                       |
| POST   | `/api/profile` | Save user profile                         |

## Rebuilding the Knowledge Base

To update the RAG index after adding/removing PDFs:

```bash
rm -rf backend/knowledge_base/chroma_db/
# Restart the backend - index rebuilds automatically
```

## AWS Bedrock Models Used

| Purpose    | Model ID                       |
| ---------- | ------------------------------ |
| LLM        | `amazon.nova-lite-v1:0`        |
| Embeddings | `amazon.titan-embed-text-v2:0` |

Ensure these models are enabled in your AWS Bedrock console.

## Tech Stack

**Backend:**

- FastAPI - Web framework
- LangChain - Agent orchestration
- AWS Bedrock - LLM & embeddings
- ChromaDB - Vector database
- Pydantic - Data validation

**Frontend:**

- React 18 - UI framework
- Vite - Build tool
- TailwindCSS - Styling
- Axios - HTTP client
- react-markdown - Markdown rendering
- lucide-react - Icons

## License

MIT
