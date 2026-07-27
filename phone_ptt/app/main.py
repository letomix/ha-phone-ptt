import os
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# Garante que a pasta static existe para evitar RuntimeError
os.makedirs("/app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Interface Web Integrada (Funciona em qualquer browser, PC e telemóvel via Ingress)
HTML_PADAO = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home Assistant PTT</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--card-background-color, #111111);
            color: var(--primary-text-color, #e1e1e1);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: var(--ha-card-background, #1c1c1c);
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            width: 90%;
            max-width: 400px;
            text-align: center;
        }
        select, button {
            width: 100%;
            padding: 14px;
            margin-top: 15px;
            border-radius: 8px;
            border: 1px solid var(--divider-color, #333);
            font-size: 16px;
            box-sizing: border-box;
        }
        select {
            background: var(--card-background-color, #222);
            color: var(--primary-text-color, #fff);
        }
        #ptt-btn {
            background-color: var(--primary-color, #03a9f4);
            color: white;
            border: none;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.2s;
            user-select: none;
            -webkit-user-select: none;
        }
        #ptt-btn.recording {
            background-color: #db4437 !important;
        }
        #status {
            margin-top: 15px;
            font-size: 13px;
            color: var(--secondary-text-color, #888);
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Push-to-Talk</h2>
        <p style="font-size: 14px;">Selecione o altifalante e mantenha premido para falar:</p>
        
        <select id="ptt-player">
            <option value="media_player.cuisine">Cuisine</option>
            <option value="media_player.corredor_2">Corredor 2</option>
            <option value="media_player.grupo_casa">Grupo Casa</option>
            <option value="media_player.tv_do_salao">TV do Salão</option>
        </select>

        <button id="ptt-btn">🎙️ Pressionar para Falar</button>
        <p id="status">Toque no botão para ativar o microfone.</p>
    </div>

    <script>
        const btn = document.getElementById('ptt-btn');
        const status = document.getElementById('status');
        const playerSelect = document.getElementById('ptt-player');
        let mediaRecorder;
        let audioChunks = [];

        async function init() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    status.innerText = "A enviar áudio...";
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    audioChunks = [];

                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'ptt.wav');
                    formData.append('player', playerSelect.value);

                    try {
                        const response = await fetch('/speak', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();
                        if (result.success) {
                            status.innerText = "Áudio enviado com sucesso!";
                        } else {
                            status.innerText = "Erro ao reproduzir no altifalante.";
                        }
                    } catch (err) {
                        status.innerText = "Erro de rede ao enviar o áudio.";
                    }
                };
                status.innerText = "Pronto. Mantenha premido para falar.";
            } catch (e) {
                status.innerText = "Erro: Permissão de microfone negada.";
            }
        }

        btn.addEventListener('click', () => {
            if (!mediaRecorder) init();
        }, { once: true });

        // Eventos para rato (PC)
        btn.addEventListener('mousedown', () => {
            if (mediaRecorder && mediaRecorder.state === 'inactive') {
                audioChunks = [];
                mediaRecorder.start();
                btn.classList.add('recording');
                status.innerText = "A gravar... Fale agora.";
            }
        });

        btn.addEventListener('mouseup', () => {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                btn.classList.remove('recording');
            }
        });

        // Eventos para toque (Telemóvel / Touchscreen)
        btn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (!mediaRecorder) {
                init();
            } else if (mediaRecorder.state === 'inactive') {
                audioChunks = [];
                mediaRecorder.start();
                btn.classList.add('recording');
                status.innerText = "A gravar... Fale agora.";
            }
        });

        btn.addEventListener('touchend', (e) => {
            e.preventDefault();
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                btn.classList.remove('recording');
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PADAO

@app.post("/speak")
async def speak(audio: UploadFile = File(...), player: str = Form(...)):
    try:
        file_path = f"/app/static/{audio.filename}"
        with open(file_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        # Aqui o ficheiro está pronto a ser enviado para o Home Assistant media_player escolhido (`player`)
        print(f"Áudio recebido para o leitor: {player} guardado em {file_path}")
        
        return JSONResponse({"success": True, "player": player})
    except Exception as e:
        return JSONResponse({"success": False, "detail": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8099)
