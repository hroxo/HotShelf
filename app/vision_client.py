# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vision_client.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: hroxo <hroxo@student.42porto.com>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/11/11 21:28:13 by hroxo             #+#    #+#              #
#    Updated: 2025/11/12 11:40:51 by hroxo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import json, re
from typing import List, Dict
from openai import AzureOpenAI
from .env import (
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT, TEMPERATURE, MAX_TOKENS
)

def _client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )

def call_vision(user_content: list, use_json_mode: bool = True) -> str:
    client = _client()
    kwargs = {
        "model": AZURE_OPENAI_DEPLOYMENT,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": "placeholder"},  # substituído abaixo
            {"role": "user",   "content": user_content},
        ]
    }
    # definimos o system no final para manter legibilidade
    return kwargs, client

def complete(system_prompt: str, user_content: list, use_json_mode: bool = True) -> str:
    client = _client()
    kwargs = {
        "model": AZURE_OPENAI_DEPLOYMENT,
        "temperature": TEMPERATURE,   # recomendo 0.1–0.2 para menos alucinação
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content},
        ],
    }
    if use_json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""

def parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
        if not m: raise
        return json.loads(m.group(0))
