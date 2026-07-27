from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Phone PTT</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #111111;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
            touch-action: manipulation;
        }
        .container {
            text-align: center;
            width: 90%;
            max-width: 400px;
        }
        select {
            width: 100%;
            padding: 14px;
            font-size: 16px;
            border-radius: 12px;
            background: #222222;
            color: #ffffff;
            border: 1px solid #444;
            margin-bottom: 30px;
            outline: none;
        }
        #ptt-btn {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: #03a9f4;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border: none;
            box-shadow: 0 8px 20px rgba(3, 169, 244, 0.4);
            cursor: pointer;
            outline: none;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }
        #status {
            margin-top: 25px;
            font-size: 15px;
            color: #b0bec5;
            min-height: 24px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Push-to-Talk</h2>
        <select id="ptt-player">
            <option value="media_player.grupo_casa">Grupo Casa (Todos)</option>
            <option value="media_player.cuisine">Cozinha</option>
            <option value="media_player.corredor_2">Corredor</option>
            <option value="media_player.tv_do_salao">TV Salão</option>
        </select>
        
        <!-- Botão com eventos integrados diretamente para garantir resposta imediata -->
        <button id="ptt-btn" 
                onmousedown="startRecording(event)" 
                onmouseup="stopRecording(event)" 
                ontouchstart="startRecording(event)" 
                ontouchend="stopRecording(event)">GRAVAR</button>
        <div id="status">Sistema pronto. Toque para falar</div>
    </div>

    <script>
        const status = document.getElementById('status');
        const playerSelect = document.getElementById('ptt-player');
        let mediaRecorder = null;
        let audioChunks = [];

        async function startRecording(e) {
            e.preventDefault();
            status.innerText = "A iniciar gravação...";

            try {
                if (!mediaRecorder) {
                    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                        status.innerText = "Erro: Microfone não suportado.";
                        return;
                    }
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = async () => {
                        status.innerText = "A enviar áudio...";
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        audioChunks = [];

                        const formData = new FormData();
                        formData.append('audio', audioBlob, 'ptt.webm');
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
                                status.innerText = "Erro no servidor.";
                            }
                        } catch (err) {
                            status.innerText = "Erro de rede ao enviar.";
                        }
                    };
                }

                if (mediaRecorder.state === 'inactive') {
                    audioChunks = [];
                    mediaRecorder.start();
                    status.innerText = "A gravar... Fale agora!";
                }
            } catch (err) {
                console.error(err);
                status.innerText = "Erro: Permissão de microfone negada.";
            }
        }

        function stopRecording(e) {
            e.preventDefault();
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_CONTENT

@app.post("/speak")
async def speak(audio: UploadFile = File(...), player: str = Form(...)):
    contents = await audio.read()
    print(f"Áudio recebido com sucesso! Tamanho: {len(contents)} bytes para o leitor: {player}")
    return {"success": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8099)
