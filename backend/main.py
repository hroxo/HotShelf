import asyncio
import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# ------------------ util ------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def status_from_score(score: int) -> str:
    if score <= 0: return "empty"
    if score <= 20: return "low"
    if score >= 60: return "full"
    return "ok"

def to_sse_event(data: dict) -> bytes:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


# ------------------ app ------------------
app = FastAPI(title="Realtime Camera Backend", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LAST_STATE: Dict[str, Dict[str, Any]] = {}
SUBSCRIBERS: Dict[str, List[asyncio.Queue]] = defaultdict(list)


@app.get("/health")
def health():
    return {"ok": True, "time": now_iso()}


@app.get("/state/{camera_id}")
def get_state(camera_id: str):
    return LAST_STATE.get(camera_id, {"camera_id": camera_id, "message": "sem dados ainda"})


@app.get("/sse/cameras/{camera_id}")
async def sse_camera(camera_id: str):
    q: asyncio.Queue = asyncio.Queue()
    SUBSCRIBERS[camera_id].append(q)

    if camera_id in LAST_STATE:
        await q.put(LAST_STATE[camera_id])

    async def event_stream():
        try:
            while True:
                event = await q.get()
                yield to_sse_event(event)
        finally:
            try:
                SUBSCRIBERS[camera_id].remove(q)
            except ValueError:
                pass

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def _broadcast(camera_id: str, event: Dict[str, Any]):
    LAST_STATE[camera_id] = event
    for q in list(SUBSCRIBERS.get(camera_id, [])):
        await q.put(event)


# ------------------ INGEST ------------------
@app.post("/ingest")
async def ingest(req: Request):

    try:
        body = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON inválido: {e}")

    detections = body.get("detections")
    if not isinstance(detections, list):
        raise HTTPException(status_code=400, detail="esperado objeto com detections[]")

    # agrupar por câmara
    by_cam: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for d in detections:
        cam = str(d.get("camera_id", ""))
        if cam:
            by_cam[cam].append(d)

    if not by_cam:
        return {"status": "ok", "cameras": 0}

    emitted = 0

    # processar cada câmara
    for camera_id, dets in by_cam.items():

        # ---- enriquecer cada detecção ----
        enriched = []
        for d in dets:
            score = int(d.get("pontuacao_total", 0))
            status = status_from_score(score)

            quad_raw = d.get("roi_quad_px") or {}
            quad = [
                quad_raw.get("top_left"),
                quad_raw.get("top_right"),
                quad_raw.get("bottom_right"),
                quad_raw.get("bottom_left"),
            ]

            enriched.append({
                "id": f"{camera_id}|{d.get('roi_id')}",
                "camera_id": camera_id,
                "image_name": d.get("image_name"),
                "roi_id": d.get("roi_id"),
                "product_id": d.get("product_id"),
                "product_name": d.get("product_name"),
                "fruit_type": d.get("fruit_type"),

                # novas métricas
                "quantidade_pct": d.get("quantidade_pct"),
                "qualidade_pct": d.get("qualidade_pct"),
                "organizacao_pct": d.get("organizacao_pct"),
                "contexto_pct": d.get("contexto_pct"),
                "indice_var": d.get("indice_var"),

                "score": score,
                "status": status,
                "confidence": float(d.get("confidence", 0.0)),
                "insights": d.get("insights"),
                "quad": quad,
                "ui": {
                    "color": {
                        "empty": "#E53935",
                        "low":   "#FB8C00",
                        "ok":    "#FDD835",
                        "full":  "#43A047",
                    }[status]
                }
            })

        # ---- resumo por produto ----
        summary_map: Dict[str, Dict[str, Any]] = {}
        for e in enriched:
            pid = e["product_id"]
            rec = summary_map.setdefault(pid, {
                "product_id": pid,
                "product_name": e["product_name"],
                "count": 0,
                "sum_score": 0,
                "sum_quantidade": 0,
                "sum_qualidade": 0,
                "sum_organizacao": 0,
                "sum_contexto": 0,
                "min_score": 10**9,
                "max_score": -10**9,
                "empties": 0, "lows": 0, "oks": 0, "fulls": 0,
            })

            sc = e["score"]
            rec["count"] += 1
            rec["sum_score"] += sc
            rec["min_score"] = min(rec["min_score"], sc)
            rec["max_score"] = max(rec["max_score"], sc)
            rec["sum_quantidade"] += e.get("quantidade_pct") or 0
            rec["sum_qualidade"] += e.get("qualidade_pct") or 0
            rec["sum_organizacao"] += e.get("organizacao_pct") or 0
            rec["sum_contexto"] += e.get("contexto_pct") or 0
            rec[{"empty":"empties","low":"lows","ok":"oks","full":"fulls"}[e["status"]]] += 1

        summary = []
        for rec in summary_map.values():
            count = rec["count"]
            summary.append({
                "product_id": rec["product_id"],
                "product_name": rec["product_name"],
                "count": rec["count"],
                "avg_score": rec["sum_score"] / count,
                "min_score": rec["min_score"],
                "max_score": rec["max_score"],
                "avg_quantidade_pct": rec["sum_quantidade"] / count,
                "avg_qualidade_pct": rec["sum_qualidade"] / count,
                "avg_organizacao_pct": rec["sum_organizacao"] / count,
                "avg_contexto_pct": rec["sum_contexto"] / count,
                "empties": rec["empties"],
                "lows": rec["lows"],
                "oks": rec["oks"],
                "fulls": rec["fulls"],
            })

        # ---- FrameEvent (FALTAVA!) ----
        frame_event = {
            "type": "frame",
            "version": "1.0",
            "camera_id": camera_id,
            "observed_at": now_iso(),
            "image": {},
            "detections": enriched,
            "summary": summary,
        }

        await _broadcast(camera_id, frame_event)
        emitted += 1

    return {"status": "ok", "cameras": len(by_cam), "events_emitted": emitted}
