# app/main.py
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: hroxo <hroxo@student.42porto.com>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/11/12 19:07:12 by hroxo             #+#    #+#              #
#    Updated: 2025/11/13  xx:xx:xx by hroxo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import json, io, time, os, datetime
from collections import Counter
from PIL import Image

from .env import CROPS_PREFIX, ROI_JSON_BLOB, OAI_ROI_BATCH
from .blob_io import (
    list_all_images,      # novo: lista todas as imagens no blob (fora de crops/)
    download_image,       # novo: download de uma imagem específica
    read_blob_bytes,
    upload_bytes_many,
    make_sas_url,
)
from .snip import warp_quad_to_bytes
from .prompt import SYSTEM_PROMPT_ROI, build_user_content_for_rois
from .vision_client import complete, parse_json
from .weight import compute_final_scores
from .concat_json import concat_json_files


# -------------------------------------------------------------------------
# Helpers: ler JSON de ROIs
# -------------------------------------------------------------------------
def load_roi_json_local(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_roi_json():
    """
    Carrega JSON de ROIs do blob (se ROI_JSON_BLOB definido)
    ou de um ficheiro local 'utils/plantest.json'.
    """
    if ROI_JSON_BLOB:
        data = read_blob_bytes(ROI_JSON_BLOB)
        return json.loads(data.decode("utf-8"))
    return load_roi_json_local("utils/plantest.json")


# -------------------------------------------------------------------------
# Helpers: mapear imagem -> camera_id e extrair ROIs
# -------------------------------------------------------------------------
def get_camera_id_from_filename(filename: str) -> str:
    """
    Nome da imagem é literalmente o número da câmara.
    Ex.: '6215.jpg' → '6215'
    """
    base = os.path.basename(filename)
    cam_id, _ext = os.path.splitext(base)
    return cam_id

def extract_rois_flex(camera_json, image_name):
    """
    Extrai apenas as ROIs da câmara correspondente ao nome da imagem.
    Ex.: '6215.jpg' → usa camera_id '6215' em camera_json['Frutas e Legumes']['cameras']['6215']
    """
    cam_id = get_camera_id_from_filename(image_name)

    # localizar bloco 'cameras'
    cams = None
    if isinstance(camera_json, dict):
        root = camera_json.get("Frutas e Legumes", camera_json)
        if isinstance(root, dict) and "cameras" in root and isinstance(root["cameras"], dict):
            cams = root["cameras"]

    if not isinstance(cams, dict):
        print("[ROI] ⚠️ JSON não contém bloco 'cameras'.")
        return []

    if cam_id not in cams:
        print(f"[ROI] ⚠️ Câmara {cam_id} não encontrada no planograma → sem ROIs.")
        return []

    cam_block = cams[cam_id]
    prods = cam_block.get("products", []) if isinstance(cam_block, dict) else []

    need = {"top_left", "top_right", "bottom_right", "bottom_left"}
    rois = []

    for idx, p in enumerate(prods, start=1):
        coords = p.get("image_coordinates") or {}
        if not (isinstance(coords, dict) and need.issubset(coords.keys())):
            continue
        rois.append({
            "camera_id": cam_id,
            "image_name": image_name,
            "roi_id": f"{p.get('product_id','roi')}_{idx}",
            "product_id": p.get("product_id",""),
            "product_name": p.get("product_name",""),
            "quad": {
                "top_left": coords["top_left"],
                "top_right": coords["top_right"],
                "bottom_right": coords["bottom_right"],
                "bottom_left": coords["bottom_left"],
            }
        })

    print(f"[ROI] Câmara {cam_id}: {len(rois)} ROIs extraídas.")
    return rois


# -------------------------------------------------------------------------
# 1. Faz snip dos ROIs e sobe os crops (para UMA imagem)
# -------------------------------------------------------------------------
def run_snip_only(blob_name: str, camera_json):
    # download da imagem específica
    bytes_img, mime = download_image(blob_name)
    pil = Image.open(io.BytesIO(bytes_img)).convert("RGB")

    # extrair ROIs só da câmara correspondente a esta imagem
    rois = extract_rois_flex(camera_json, blob_name)
    if not rois:
        raise RuntimeError(f"Sem ROIs válidas no JSON para a imagem {blob_name}.")
    print(f"[ROI] {len(rois)} recortes para {blob_name}. Ex: {Counter(r['camera_id'] for r in rois)}")

    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    prefix = f"{CROPS_PREFIX}/{rois[0]['camera_id']}_{ts}"
    pairs, crop_blob_paths = [], []

    for r in rois:
        crop_bytes = warp_quad_to_bytes(
            pil, r["quad"],
            mime=("image/png" if mime == "image/png" else "image/jpeg"),
            quality=92
        )
        ext = ".png" if mime == "image/png" else ".jpg"
        blob_path = f"{prefix}/roi_{r['roi_id']}{ext}"
        pairs.append((blob_path, crop_bytes, "image/png" if ext == ".png" else "image/jpeg"))
        crop_blob_paths.append(blob_path)

    uploaded = upload_bytes_many(pairs)
    print(f"[UPLOAD] {len(uploaded)} crops → {prefix}/")

    return blob_name, rois, crop_blob_paths


# -------------------------------------------------------------------------
# 2. Classifica os crops em lotes (para UMA imagem)
# -------------------------------------------------------------------------
def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def run_snip_and_classify_for_image(blob_name: str, camera_json):
    image_name, rois, crop_blob_paths = run_snip_only(blob_name, camera_json)

    # gerar SAS URLs para os crops
    sas_urls_all = [make_sas_url(p) for p in crop_blob_paths]

    # dividir em batches
    batches_rois = list(_chunks(rois, OAI_ROI_BATCH))
    batches_sas  = list(_chunks(sas_urls_all, OAI_ROI_BATCH))
    total_batches = len(batches_rois)
    print(f"[MODEL] {blob_name}: processando {len(rois)} ROIs em {total_batches} lotes de {OAI_ROI_BATCH}...")

    all_detections, raw_dumps = [], []

    for bi, (rois_batch, sas_batch) in enumerate(zip(batches_rois, batches_sas), start=1):
        print(f"[MODEL] {blob_name} → Lote {bi}/{total_batches} ({len(rois_batch)} ROIs)")
        user_content = build_user_content_for_rois(rois_meta=rois_batch, sas_urls=sas_batch)
        raw = complete(SYSTEM_PROMPT_ROI, user_content, use_json_mode=True)
        raw_dumps.append(raw)
        try:
            obj = parse_json(raw)
        except Exception:
            obj = json.loads(raw)

        # normaliza formato
        if isinstance(obj, list):
            dets = obj
        elif isinstance(obj, dict) and "detections" in obj:
            dets = obj["detections"]
        else:
            dets = [obj]
        if not isinstance(dets, list):
            dets = [dets]
        all_detections.extend(dets)

    # agrega e CALCULA o índice final antes de gravar
    results = {"detections": all_detections}
    results = compute_final_scores(results)

    # persistência — 1 ficheiro por imagem/câmara
    os.makedirs("data/input", exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    base = os.path.splitext(os.path.basename(blob_name))[0]  # ex.: '6215'
    out_json = f"data/input/{base}_roi_response_{ts}.json"

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[MODEL] {blob_name} ✓ {len(all_detections)} detections em {total_batches} lotes → {out_json}")


# -------------------------------------------------------------------------
# 3. Loop para TODAS as imagens do Blob (fora de crops/)
# -------------------------------------------------------------------------
def run_for_all_images():
    camera_json = load_roi_json()
    image_names = list_all_images()  # implementado em blob_io, ignora crops/

    if not image_names:
        print("[BATCH] Nenhuma imagem encontrada no blob (fora de 'crops/').")
        return

    print(f"[BATCH] Encontradas {len(image_names)} imagens para processar.")
    for i, blob_name in enumerate(image_names, start=1):
        print(f"\n[BATCH] ({i}/{len(image_names)}) → {blob_name}")
        try:
            run_snip_and_classify_for_image(blob_name, camera_json)
        except Exception as e:
            print(f"[BATCH] ERRO na imagem {blob_name}: {e}")


# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    run_for_all_images()
    concat_json_files()
