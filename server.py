"""
OGGY X Assistant Server
FastAPI Web Server providing REST endpoints and static file hosting.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from assistant_service import process_user_query, get_gemini_api_key, set_gemini_api_key
from knowledge_base import FEED_QA

app = FastAPI(title="OGGY X Assistant API")

# Enable Cross-Origin Resource Sharing (CORS) for flexible deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_CACHE_DIR = os.path.join(STATIC_DIR, "audio_cache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

class AskRequest(BaseModel):
    query: str

class ConfigRequest(BaseModel):
    gemini_api_key: str

@app.get("/")
async def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "OGGY X Assistant Backend Running"}

@app.post("/api/ask")
async def ask_endpoint(payload: AskRequest):
    result = await process_user_query(payload.query)
    return result

@app.get("/api/config")
async def get_config():
    key = get_gemini_api_key()
    masked = ""
    if key:
        if len(key) > 8:
            masked = key[:4] + "*" * (len(key) - 8) + key[-4:]
        else:
            masked = "****"
    return {
        "has_gemini_key": bool(key),
        "masked_key": masked
    }

@app.post("/api/config")
async def set_config(payload: ConfigRequest):
    set_gemini_api_key(payload.gemini_api_key)
    return {
        "status": "success",
        "has_gemini_key": bool(payload.gemini_api_key.strip())
    }

@app.get("/api/suggestions")
async def get_suggestions():
    # Return quick suggestion chips for the UI
    suggestions = [
        "Hello Oggy",
        "Open YouTube",
        "Search for space exploration",
        "Open GitHub",
        "Open Terminal",
        "Open WhatsApp",
        "Who creates you?",
        "What time is it?",
        "Tell me a joke"
    ]
    return {"suggestions": suggestions}

# Mount static files (HTML, CSS, JS, videos, images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
