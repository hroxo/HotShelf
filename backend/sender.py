import json, sys, requests

API = "http://localhost:8000/ingest"

# uso: python agent_sender.py [caminho_json]
path = sys.argv[1] if len(sys.argv) > 1 else "payload_exemplo.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

resp = requests.post(API, json=data, timeout=30)
print(resp.status_code, resp.json())
