import os
import json
import requests
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
    "Content-Type": "application/json",
}

AUDIO_DIR = "/tmp/audio_cache"
os.makedirs(AUDIO_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="/app/static"), name="static")
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("/app/static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/speak")
async def speak(audio: UploadFile = File(...), player: Form(...)):
    file_path = os.path.join(AUDIO_DIR, "message.webm")
    
    with open(file_path, "wb") as buffer:
        content = await audio.read()
        buffer.write(content)

    addon_host = os.environ.get("HOSTNAME", "localhost")
    audio_url = f"http://{addon_host}:8099/audio/message.webm"

    ha_url = "http://supervisor/core/api/services/media_player/play_media"
    payload = {
        "entity_id": player,
        "media_content_id": audio_url,
        "media_content_type": "music"
    }

    response = requests.post(ha_url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return JSONResponse({"status": "success", "message": "Áudio enviado com sucesso!"})
    else:
        return JSONResponse({"status": "error", "message": response.text}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8099)
