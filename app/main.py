import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()

# Criar pasta de cache de áudio local
AUDIO_DIR = "/tmp/audio_cache"
os.makedirs(AUDIO_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
    "Content-Type": "application/json",
}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    html_path = "/app/static/index.html"
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Interface PTT não encontrada</h1>"

@app.get("/api/media_players")
async def get_media_players():
    try:
        response = requests.get("http://supervisor/core/api/states", headers=HEADERS, timeout=5)
        if response.status_code == 200:
            states = response.json()
            players = [
                state["entity_id"] for state in states 
                if state["entity_id"].startswith("media_player.")
            ]
            return {"players": players}
    except Exception as e:
        print(f"Erro ao buscar media players: {e}")
    return {"players": []}

@app.post("/api/upload_audio")
async def upload_audio(file: UploadFile = File(...), target_player: str = Form(...)):
    file_path = os.path.join(AUDIO_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Obter URL externa/interna do add-on se necessário ou usar o fluxo do supervisor
    # Para simplificar o envio local para o media_player:
    # Disparar serviço play_media no Home Assistant Core
    service_data = {
        "entity_id": target_player,
        "media_content_id": f"http://127.0.0.1:8099/audio/{file.filename}",
        "media_content_type": "music"
    }
    
    try:
        requests.post(
            f"http://supervisor/core/api/services/media_player/play_media",
            headers=HEADERS,
            json=service_data,
            timeout=5
        )
    except Exception as e:
        print(f"Erro ao disparar player: {e}")

    return {"status": "success", "message": "Áudio transmitido com sucesso!"}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(AUDIO_DIR, filename))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8099)
