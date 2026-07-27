FROM alpine:3.19

# Instalar o Python 3, Pip e dependências essenciais do sistema
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash

# Definir o diretório de trabalho
WORKDIR /app

# Instalar o FastAPI e Uvicorn diretamente (ou via requirements.txt se preferir)
RUN pip3 install --no-cache-dir --break-system-packages fastapi uvicorn

# Copiar o script principal para a raiz do diretório de trabalho
COPY main.py /app/main.py

# Criar a pasta static exigida pelo FastAPI para evitar erros em runtime
RUN mkdir -p /app/static

# O Python torna-se imediatamente o PID 1 absoluto
ENTRYPOINT ["python3"]
CMD ["/app/main.py"]
