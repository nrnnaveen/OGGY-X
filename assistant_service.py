"""
Assistant Service for OGGY X
Orchestrates knowledge base feed queries and optional Google Gemini API fallback.
"""

import os
import json
import logging
import asyncio
import httpx
from knowledge_base import find_feed_answer, get_fallback_answer, launch_local_app

logger = logging.getLogger("oggy_assistant")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

OGGY_SYSTEM_PROMPT = (
    "You are OGGY X, the upgraded, super-smart, hilarious cartoon AI cat version of Oggy from "
    "'Oggy and the Cockroaches'. You are friendly, witty, enthusiastic, and love chatting with humans. "
    "Keep all your answers concise and punchy (1 to 3 sentences maximum) so it flows naturally in spoken conversation. "
    "Sprinkle in cartoonish humor, cat expressions (Meow, *chuckles*, *paws up*), and references to your fridge or pesky roaches when appropriate."
)

def get_gemini_api_key() -> str:
    # 1. Environment variable
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        return api_key

    # 2. Local config.json
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("gemini_api_key", "").strip()
        except Exception:
            pass
    return ""

def set_gemini_api_key(api_key: str):
    data = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data["gemini_api_key"] = api_key.strip()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


async def ask_gemini(query: str, api_key: str) -> dict:
    """
    Call Google Gemini API using REST endpoint.
    Uses gemini-2.5-flash (or gemini-1.5-flash).
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {
            "parts": [{"text": OGGY_SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": query}]
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 150
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                result = resp.json()
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "").strip()
                        return {
                            "answer": text,
                            "emotion": "excited",
                            "video_style": "speaking_gesture",
                            "source": "gemini"
                        }
            else:
                logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")

    # Fallback to secondary model if 2.5-flash had an issue
    try:
        fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(fallback_url, json=payload)
            if resp.status_code == 200:
                result = resp.json()
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "").strip()
                        return {
                            "answer": text,
                            "emotion": "excited",
                            "video_style": "speaking_gesture",
                            "source": "gemini"
                        }
    except Exception as e:
        logger.error(f"Secondary model error: {e}")

    return None


import hashlib
import edge_tts

AUDIO_CACHE_DIR = os.path.join(os.path.dirname(__file__), "static", "audio_cache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

async def generate_speech_audio(text: str) -> str:
    """
    Generate realistic cartoon voice MP3 using edge-tts with strict timeout.
    If network is slow or times out, immediately returns empty string
    so browser instantly uses local speech synthesis.
    """
    filepath = ""
    try:
        clean_text = text.replace("*", "").strip()
        h = hashlib.md5(clean_text.encode("utf-8")).hexdigest()
        filename = f"{h}.mp3"
        filepath = os.path.join(AUDIO_CACHE_DIR, filename)
        
        # If valid cached file exists with content, return immediately
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return f"/static/audio_cache/{filename}"

        communicate = edge_tts.Communicate(clean_text, "en-US-GuyNeural", pitch="+20Hz", rate="+12%")
        
        # 4.0s timeout: gives enough time for first-time websocket, while failing fast if offline
        await asyncio.wait_for(communicate.save(filepath), timeout=4.0)

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return f"/static/audio_cache/{filename}"
        else:
            if os.path.exists(filepath):
                os.remove(filepath)
            return ""
    except Exception as e:
        logger.warning(f"edge-tts unavailable or timed out ({e}); failing fast for instant local browser speech")
        if filepath and os.path.exists(filepath) and os.path.getsize(filepath) == 0:
            try:
                os.remove(filepath)
            except Exception:
                pass
        return ""

async def process_user_query(query: str) -> dict:
    """
    Main resolution engine:
    1. Knowledge Base Feed match
    2. Optional Gemini API call
    3. Witty Oggy Fallback
    4. Generate realistic cartoon voice audio
    """
    query_str = (query or "").strip()
    result = None

    # Step 1: Check knowledge base feed
    feed_res = find_feed_answer(query_str)
    if feed_res and feed_res.get("matched"):
        feed_res["source"] = "feed"
        result = feed_res
        
        # If action is a local desktop application, spawn it on the system
        if result.get("action", {}).get("type") == "local_app":
            cmd = result["action"].get("cmd")
            if cmd:
                launch_local_app(cmd)

    # Step 2: Check Gemini API Key if available
    if not result:
        api_key = get_gemini_api_key()
        if api_key:
            gemini_res = await ask_gemini(query_str, api_key)
            if gemini_res:
                result = gemini_res

    # Step 3: Witty cartoon fallback
    if not result:
        fallback_res = get_fallback_answer()
        fallback_res["source"] = "fallback"
        result = fallback_res

    # Step 4: Generate neural cartoon voice audio
    if result and result.get("answer"):
        result["audio_url"] = await generate_speech_audio(result["answer"])

    return result
