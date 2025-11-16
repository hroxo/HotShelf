# file_poller.py
import argparse, json, time
from pathlib import Path
import requests

def is_final_json(p: Path):
    return p.suffix == ".json" and ".raw." not in p.name and not p.name.endswith(".raw.json")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/outputs")
    # aqui já podemos colocar o default certo para docker:
    ap.add_argument("--backend", default="http://backend:8000/ingest")
    ap.add_argument("--pattern", default="roi_response_*.json")
    ap.add_argument("--interval", type=float, default=1.0)
    args = ap.parse_args()

    seen = set()
    dirp = Path(args.dir)
    if not dirp.exists():
        print(f"não existe: {dirp}")
        return

    # envia o mais recente na partida
    files = [p for p in dirp.glob(args.pattern) if is_final_json(p)]
    if files:
        latest = max(files, key=lambda p: p.stat().st_mtime)
        try:
            with open(latest, "r", encoding="utf-8") as f:
                data = json.load(f)
            requests.post(args.backend, json=data, timeout=15)
            seen.add(latest.resolve())
        except Exception as e:
            print(f"[WARN] falha enviando inicial {latest}: {e}")

    print(f"[polling] {dirp} (cada {args.interval}s)")
    last_mtime = 0
    while True:
        for p in dirp.glob(args.pattern):
            if not is_final_json(p): 
                continue
            rp = p.resolve()
            mtime = p.stat().st_mtime
            if rp not in seen and mtime > last_mtime:
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    requests.post(args.backend, json=data, timeout=15)
                    print(f"[OK] {p.name}")
                    seen.add(rp)
                    last_mtime = mtime
                except Exception as e:
                    print(f"[WARN] falha lendo {p}: {e}")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
