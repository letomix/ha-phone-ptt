FROM alpine:3.19

# Instalar o Python 3, Pip e dependências essenciais do sistema
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências de Python se existirem
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt || true

# Copiar os ficheiros da aplicação
COPY app/ /app/

# O Python torna-se imediatamente o PID 1 absoluto (sem s6-overlay pelo meio)
ENTRYPOINT ["python3"]
CMD ["/app/main.py"]
