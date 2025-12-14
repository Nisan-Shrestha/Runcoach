import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agent import agent
from rag import rag

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="RunCoach AI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---

class UserProfile(BaseModel):
    name: Optional[str] = ""
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    experience_level: str = "beginner"
    weekly_mileage: Optional[float] = None
    goal: str = "5K"
    dietary_preference: str = "none"
    training_days: int = 3
    location: str = ""


class ChatMessage(BaseModel):
    message: str
    user_profile: Optional[UserProfile] = None


class ChatResponse(BaseModel):
    response: str
    success: bool


# --- Storage ---
user_profiles = {}


# --- Events ---

@app.on_event("startup")
async def startup():
    logger.info("\n🚀 Starting RunCoach AI...")
    logger.info("=" * 40)
    try:
        rag.setup()
        agent.setup()
        logger.info("=" * 40)
        logger.info("✅ Server ready!\n")
    except Exception as e:
        logger.error(f"⚠️ Startup error: {e}")


# --- Endpoints ---

@app.get("/")
async def health():
    return {"status": "healthy", "message": "RunCoach AI is running! 🏃"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(msg: ChatMessage):
    """Main chat endpoint"""
    try:
        profile = msg.user_profile.model_dump() if msg.user_profile else None
        result = agent.chat(msg.message, profile)
        return ChatResponse(response=result["response"], success=result["success"])
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/profile")
async def save_profile(profile: UserProfile):
    """Save user profile"""
    user_profiles["current"] = profile.model_dump()
    return {"message": "Profile saved!", "profile": profile}


@app.get("/api/profile")
async def get_profile():
    """Get current user profile"""
    return user_profiles.get("current", {})


@app.post("/api/reset")
async def reset():
    """Reset conversation"""
    agent.reset_memory()
    return {"message": "Chat history cleared!"}


@app.get("/api/search")
async def search(query: str):
    """Direct knowledge base search"""
    try:
        context, sources = rag.search(query, k=3)
        return {"results": context, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quick-questions")
async def quick_questions():
    """Predefined quick questions"""
    return {
        "questions": [
            "🏃 How do I start running as a beginner?",
            "🍎 What should I eat before a run?",
            "💪 Create a training plan for me",
            "🤕 How can I prevent injuries?",
            "⏱️ What's a good warm-up routine?",
            "🎯 Help me prepare for a 5K",
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
