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

# Copiar a arquitetura de arranque do s6-overlay para o sistema do container
COPY rootfs /

# Deixar o CMD vazio ou sem diretivas complexas, pois o s6-overlay gere o ciclo de vida nativamente através do rootfs
CMD ["/init"]
