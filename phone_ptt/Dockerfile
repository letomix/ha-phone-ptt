FROM alpine:3.19

# Instalar o Python 3, Pip e dependências essenciais do sistema
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash

# Definir o diretório de trabalho
WORKDIR /app

# Instalar pacotes necessários do Python diretamente
RUN pip3 install --no-cache-dir --break-system-packages fastapi uvicorn

# Copiar o script principal para o container
COPY main.py /app/main.py

# Criar a pasta static por precaução
RUN mkdir -p /app/static

# Executar a aplicação Python diretamente como PID 1
ENTRYPOINT ["python3"]
CMD ["/app/main.py"]
