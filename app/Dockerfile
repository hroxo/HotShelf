# app/Dockerfile  → imagem do AGENTE (snip + Azure OpenAI)

FROM python:3.10-slim

# boas práticas para Python em container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# diretório base da app dentro do container
WORKDIR /app

# requirements está em utils/requirements.txt no HOST
COPY utils/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# copia o código do agente, utils e backend (para usar backend.file_poller)
COPY app ./app
COPY utils ./utils
COPY backend ./backend

# copia o entrypoint do agente
COPY ./backend/agent_entrypoint.sh ./agent_entrypoint.sh
RUN chmod +x ./agent_entrypoint.sh

# cria pasta de outputs (vai ser montada em /app/data pelo compose)
RUN mkdir -p /app/data/outputs

# user não-root (boa prática de segurança)
RUN useradd -m runner && chown -R runner:runner /app
USER runner

# comando por defeito → script que inicia file_poller + loop do agente
CMD ["sh", "./agent_entrypoint.sh"]
