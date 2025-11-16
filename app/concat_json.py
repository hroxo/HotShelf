import os
import json
from pathlib import Path
from datetime import datetime

INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/outputs")


def concat_json_files():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = OUTPUT_DIR / f"roi_response_{timestamp}.json"

    all_detections = []
    seen_keys = set()  # para evitar duplicados (camera_id, roi_id, image_name)

    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        print(":x: Nenhum ficheiro JSON encontrado em data/input/")
        return

    print(f":arrow_right: Encontrados {len(json_files)} ficheiros JSON.")

    for fpath in json_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            dets = data.get("detections")
            if not isinstance(dets, list):
                print(f":warning: Aviso: {fpath.name} não contém a chave 'detections' como lista")
                continue

            for d in dets:
                cam = str(d.get("camera_id", ""))
                roi = str(d.get("roi_id", ""))
                img = str(d.get("image_name", ""))

                key = (cam, roi, img)
                if key in seen_keys:
                    continue

                seen_keys.add(key)
                all_detections.append(d)

        except Exception as e:
            print(f":x: Erro ao ler {fpath.name}: {e}")

    # guardar num único ficheiro JSON
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump({"detections": all_detections}, out, ensure_ascii=False, indent=2)

    print(":white_tick: Concatenação concluída!")
    print(f":package: Total de detections (deduplicadas): {len(all_detections)}")
    print(f":floppy_disk: Guardado em: {output_file}")

    # --- LIMPAR INPUT APÓS GUARDAR OUTPUT ---
    print(":broom: A limpar ficheiros do input...")
    for fpath in json_files:
        try:
            fpath.unlink()
            print(f"   - Removido: {fpath.name}")
        except Exception as e:
            print(f":x: Erro ao remover {fpath.name}: {e}")

    print(":sparkles: Cleanup concluído! Input está agora vazio.")

