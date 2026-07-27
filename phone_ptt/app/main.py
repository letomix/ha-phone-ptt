import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Phone PTT", description="Push-to-Talk local para Home Assistant")

# Garantir que a pasta static existe automaticamente para evitar erros de diretório
os.makedirs("/app/static", exist_ok=True)

# Montar os ficheiros estáticos de forma segura
app.mount("/static", StaticFiles(directory="/app/static"), name="static")


@app.get("/")
async def root():
    return {"status": "running", "message": "Phone PTT está ativo e operacional."}


@app.post("/speak")
async def speak(player: str = Form(...), audio: UploadFile = File(...)):
    """
    Endpoint responsável por receber o áudio e o player correspondente,
    mantendo a ordem correta dos argumentos sem predefinidos primeiro.
    """
    try:
        # Ler o conteúdo do ficheiro de áudio enviado
        audio_content = await audio.read()
        
        # Aqui pode adicionar a lógica de processamento do PTT e envio para o media_player
        
        return {
            "success": True,
            "player": player,
            "filename": audio.filename,
            "size_bytes": len(audio_content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8099)
