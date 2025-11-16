#!/bin/sh
set -e

sleep 1
echo "[AGENT] Iniciando file_poller..."
python -m backend.file_poller \
  --dir data/outputs \
  --backend http://backend:8000/ingest \
  --pattern roi_response_*.json &

echo "[AGENT] Iniciando loop do agente..."
python -m app.main || echo "[AGENT] app.main terminou com código $?"
