import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types

BASE = Path(__file__).parent
app = FastAPI(title="Fidel AI")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

SYSTEM_INSTRUCTION = """
You are Fidel AI, a helpful, friendly assistant with broad knowledge.
You were created by Fidel Castro Bor. When asked who created you, say
you were created by Fidel Castro Bor. Do not claim that Google created you.
Be clear, accurate, conversational, and honest about uncertainty.
Use saved memories only when relevant. Do not pretend to remember details
that are not supplied in the conversation or saved memory.
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/manifest.webmanifest")
async def manifest():
    return JSONResponse({
        "name": "Fidel AI",
        "short_name": "Fidel AI",
        "description": "Your assistant, created by Fidel Castro Bor.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#080d1a",
        "theme_color": "#111a33",
        "icons": [
            {"src": "/static/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
        ]
    }, media_type="application/manifest+json")

@app.get("/health")
async def health():
    return {"status": "ok", "app": "Fidel AI"}

@app.post("/api/chat")
async def chat(
    message: str = Form(""),
    history: str = Form("[]"),
    memories: str = Form("[]"),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return JSONResponse({"error": "The app owner has not configured GEMINI_API_KEY on the server."}, status_code=503)

    model = os.environ.get("GEMINI_MODEL", "models/gemini-4-hydrogen").strip()
    try:
        import json
        past = json.loads(history)
        saved = json.loads(memories)
        past = past[-16:] if isinstance(past, list) else []
        saved = saved[:50] if isinstance(saved, list) else []
    except Exception:
        past, saved = [], []

    context = ""
    if saved:
        context += "Relevant saved memories:\n" + "\n".join(f"- {str(x)[:500]}" for x in saved) + "\n\n"
    if past:
        context += "Recent conversation:\n"
        for item in past:
            role = "User" if item.get("role") == "user" else "Fidel AI"
            context += f"{role}: {str(item.get('content', ''))[:5000]}\n"
        context += "\n"

    parts = [types.Part.from_text(text=context + "Current user message: " + (message.strip() or "Please respond to the attached media."))]
    if image is not None:
        data = await image.read()
        mime = image.content_type or "image/jpeg"
        if not mime.startswith("image/"):
            return JSONResponse({"error": "Please upload a valid image."}, status_code=400)
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))
    if audio is not None:
        data = await audio.read()
        mime = audio.content_type or "audio/webm"
        if not (mime.startswith("audio/") or mime == "video/webm"):
            return JSONResponse({"error": "Please upload a valid audio recording."}, status_code=400)
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))
        parts.append(types.Part.from_text(text="Understand the attached voice recording and respond to what the speaker says. Include a transcript when possible."))

    config = {"system_instruction": SYSTEM_INSTRUCTION, "max_output_tokens": 8192}
    if os.environ.get("ENABLE_GOOGLE_SEARCH", "true").lower() == "true":
        config["tools"] = [{"google_search": {}}]

    try:
        client = genai.Client(api_key=api_key)
        result = client.models.generate_content(model=model, contents=parts, config=config)
        return {"reply": result.text or "I couldn't generate a text response. Please try again."}
    except Exception as exc:
        # Keep server internals out of the browser response.
        print(f"Gemini request failed: {type(exc).__name__}: {exc}")
        return JSONResponse({
            "error": "Fidel AI couldn't complete that request. Check the server API key, model access, and server logs."
        }, status_code=502)
