ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# Instalar dependências de sistema necessárias
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-virtualenv \
        bash

# Definir o diretório de trabalho
WORKDIR /app

# Criar ambiente virtual e instalar dependências
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar os ficheiros da aplicação
COPY app/ /app/
COPY run.sh /
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
