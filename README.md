# 🦆 **42 Ducks Hackathon — SONAE Retail Visual Intelligence**

## 🧠 Overview

Projeto desenvolvido para a **SONAE** no âmbito do **Hackathon da SONAE c/ 42 Porto**.  
O objetivo é criar um **Agente de Inteligência Artificial Visual** que analisa imagens de expositores de frutas e legumes e calcula um **índice de atratividade** que indica a necessidade de reposição de produtos.

A solução combina:

- 📸 **Azure OpenAI (GPT‑4o Mini)**
- ☁️ **Azure Blob Storage**
- 🧮 **Python Agent** (snip → análise → scoring)
- 🌐 **Backend FastAPI com SSE**
- 📊 **Frontend / Dashboard (em desenvolvimento)**

---

## 🎯 Objetivo do Produto

O **Agente 42 Ducks** permite às equipas de loja:

- Monitorizar a **atratividade visual** dos expositores em tempo real
- Receber alertas de **reposição necessária**
- Visualizar um **score 0–100** (e escala 0–5) derivado de fatores estudados no Hackathon
- Correlacionar perceções visuais de consumidores com métricas de reposição

O índice foi construído com base num **estudo experimental realizado na Escola 42 Porto**, analisando sensações visuais e perceções de qualidade de frutas e vegetais.

---

## 🧱 Estrutura de Diretórios

```
app/
 ├── main.py              # Pipeline principal (snip → análise → scoring)
 ├── env.py               # Variáveis e configurações (.env)
 ├── blob_io.py           # Gestão de blobs no Azure
 ├── snip.py              # Crop/warp das ROIs (Pillow)
 ├── vision_client.py     # Cliente Azure OpenAI (retry e batch)
 ├── prompt.py            # Prompt principal (fatores 0–100)
 ├── scoring.py           # Cálculo do índice de atratividade
 └── validate_planogram.py# Validador CLI do planograma
backend/
 ├── main.py              # API FastAPI
 ├── file_poller.py       # Monitor automático de outputs
data/
 ├── input/
 ├── outputs/             # JSON final gerado pelo agente
frontend/
 ├── exec/                # Chamadas da api e dashboard 
planogram.json            # Coordenadas locais fallback
Dockerfile
backend/Dockerfile
docker-compose.yml
utils/
 ├── requirements.txt
.env
```

---

# 🚀 Setup & Execução

## 1️⃣ Ambiente virtual (modo local)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r utils/requirements.txt
```
Permissões recomendadas:

```bash
chmod -R 777 data
```

---

## 2️⃣ Executar com Docker (modo recomendado)

### 🐳 Subir a stack completa

```bash
docker compose up --build
```

Isso irá:

- Iniciar o **agente**, que processa imagens e grava JSONs em `data/outputs/`
- Iniciar o **backend**, exposto em:  
  👉 http://localhost:8000/

### 🛑 Parar

```bash
docker compose down
```

---

## 🔁 Execução automática do agente

O agente corre num loop contínuo dentro do container:

- Executa `python -m app.main`
- Aguarda **10 minutos**
- Repete

Sem necessidade de cron externo.


## 3️⃣ Configurar `.env`

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_API_VERSION=2024-08-01-preview
MAX_TOKENS=800
TEMPERATURE=0.1

# Azure Blob
AZURE_STORAGE_CONNECTION_STRING=<connection-string>
AZURE_STORAGE_ACCOUNT_KEY=<key>
BLOB_CONTAINER=hackathon

# JSON de coordenadas
ROI_JSON_BLOB=planogramas/planogram.json # vazio = fallback local

# Retry / batch
OAI_ROI_BATCH=4
OAI_MAX_RETRIES=6
OAI_BACKOFF_BASE=1.8
```

---

## 4️⃣ Executar o agente manualmente

```bash
python3 -m app.main
```

Pipeline:

1. Lê o planograma das ROIs  
2. Recorta ROIs (snip)  
3. Envia crops ao GPT‑4o mini  
4. Recebe percentuais (4 fatores)  
5. Calcula índice final  
6. Gera JSON em `data/outputs/`

---

# 🧮 Avaliação Visual

## 🎛️ Fatores avaliados pelo modelo

| Fator               | Significado                     | Guia |
|--------------------|---------------------------------|------|
| quantidade_pct     | Nível de enchimento             | <15 vazio → >90 cheio |
| qualidade_pct      | Condição visual dos produtos    | defeitos ≤5% → 90–100 |
| organizacao_pct    | Organização e acessibilidade    | caótico 0–30 → 85–100 |
| contexto_pct       | Limpeza / iluminação            | fraco 0–45 → 80–100 |

> O modelo **não retorna o índice final** — apenas percentuais.  
> O agente calcula o índice internamente.

---

## 📐 Cálculo do Índice (scoring.py)

```python
WEIGHTS = {
    "quantidade_pct": 0.50,
    "qualidade_pct": 0.35,
    "organizacao_pct": 0.10,
    "contexto_pct": 0.05,
}
```

---

# 📊 Exemplo de Saída (ROI)

```json
{
  "detections": [
    {
      "image_name": "1751001268.jpg",
      "camera_id": "6215",
      "roi_id": "20923_1",
      "product_id": "20923",
      "product_name": "BANANA DA MADEIRA CNT KG",
      "fruit_type": "banana",
      "pontuacao_total": 12,
      "quantidade_pts": 12,
      "qualidade_pts": 30,
      "organizacao_pts": 10,
      "contexto_pts": 0,
      "insights": "A esvaziar, bananas frescas, mas desorganizadas.",
      "confidence": 0.85
    },
    {
      "image_name": "1751001268.jpg",
      "camera_id": "6215",
      "roi_id": "11908_5",
      "product_id": "11908",
      "product_name": "BANANA CAT I CNT KG",
      "fruit_type": "banana",
      "pontuacao_total": 70,
      "quantidade_pts": 32,
      "qualidade_pts": 30,
      "organizacao_pts": 20,
      "contexto_pts": 10,
      "insights": "quase cheio, frutas frescas e organizadas, ambiente limpo e iluminado",
      "confidence": 0.9
    }
  ]
}
```

---

# 🌐 API — Realtime Camera Backend

## 🛰️ Visão Geral

Documentação interativa:

- 📘 Swagger → http://localhost:8000/docs  
- 📕 Redoc → http://localhost:8000/redoc  

Endpoints:

---

## ✅ **GET /health**

Verifica se o backend está online.

```json
{ "status": "ok" }
```

---

## 📌 **GET /state/{camera_id}**

Retorna o estado mais recente da câmara.

Inclui:

- Último JSON ingerido  
- Lista de deteções  
- Scores  
- Timestamp  

---

## 🔄 **GET /sse/cameras/{camera_id}**

Stream SSE para dashboards e interfaces em tempo real.

---

## 📥 **POST /ingest**

Recebe JSON gerado pelo agente.

```json
{
  "camera_id": "6215",
  "detections": [ ... ]
}
```

---

# 🔒 Gestão de Segredos & `.env`

O projeto usa chaves sensíveis (Azure OpenAI, Storage, etc.).  
Para segurança:

- `.env` **não é commitado**
- Docker **não copia** o `.env` para a imagem  
- Docker Compose injeta variáveis **apenas em runtime**
- O repo inclui um **`.env.example`**

### Criar `.env` real:

```bash
cp .env.example .env
```

### Se expuseres uma chave:

- Regenerar no Azure Portal
- Atualizar no `.env`

---

# 🎨 Frontend — Dashboard Web (React + TypeScript)

O projeto inclui um **frontend moderno desenvolvido em React + TypeScript**, utilizado pelas equipas para visualizar o estado dos expositores em tempo real.  
Ele consome diretamente a API FastAPI e o canal SSE do backend.

O frontend é servido localmente em:

```
http://localhost:5173
```

---

# 🧭 Próximos Passos

* [ ] Integração total com API FastAPI e frontend SONAE
* [ ] Dashboard com alertas automáticos
* [ ] Módulo de calibração dos pesos com feedback humano
* [ ] Pipeline contínua de ingestão e atualização de imagens

---

## 👥 Team — *42 Ducks (Escola 42 Porto)*

> Hackathon 2025 — Projeto desenvolvido para a **SONAE**
>
> 🧩 Equipa multidisciplinar da Escola 42 Porto:
>
> * **Data & AI** — tratamento, treino e pipeline de classificação
> * **DevOps** — containerização, integração com Azure
> * **Frontend** — design da interface PowerBI / WebApp (em desenvolvimento)
>
> 💙 Powered by **Azure**, **OpenAI**, e **42 Porto** and tuns of **Energy Drinks**