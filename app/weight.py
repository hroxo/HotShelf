# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    weight.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: hroxo <hroxo@student.42porto.com>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/11/12 19:39:51 by hroxo             #+#    #+#              #
#    Updated: 2025/11/13 21:59:21 by hroxo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


def compute_final_scores(results: dict) -> dict:
    """Adiciona 'pontuacao_total' (0–100) e 'indice_var' (0–5) a cada detecção."""
    WEIGHTS = {
        "quantidade_pct": 0.50,
        "qualidade_pct": 0.35,
        "organizacao_pct": 0.10,
        "contexto_pct": 0.05,
    }
    dets = results.get("detections", [])
    for d in dets:
        # clamp e ints
        qnt = max(0, min(100, int(d.get("quantidade_pct", 0))))
        qua = max(0, min(100, int(d.get("qualidade_pct", 0))))
        org = max(0, min(100, int(d.get("organizacao_pct", 0))))
        ctx = max(0, min(100, int(d.get("contexto_pct", 0))))
        total = round(
            qnt * WEIGHTS["quantidade_pct"] +
            qua * WEIGHTS["qualidade_pct"] +
            org * WEIGHTS["organizacao_pct"] +
            ctx * WEIGHTS["contexto_pct"]
        )
        d["pontuacao_total"] = max(0, min(100, total))
        d["indice_var"] = round(d["pontuacao_total"] / 20)  # compat 0–5
    return results
