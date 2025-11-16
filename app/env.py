import os
from dotenv import load_dotenv

# Carrega o ficheiro .env na inicialização
load_dotenv()

def _get(name: str, default=None, required: bool = False, cast=None):
    """Helper para ler variáveis de ambiente com cast automático."""
    val = os.getenv(name, default)
    if required and (val is None or val == ""):
        raise RuntimeError(f"Variável obrigatória ausente: {name}")
    if cast and val is not None:
        try:
            return cast(val)
        except Exception:
            raise RuntimeError(f"Erro ao converter {name}='{val}' para {cast}")
    return val


# -------------------------------------------------------------------------
# 🔷 Azure OpenAI
# -------------------------------------------------------------------------
AZURE_OPENAI_ENDPOINT    = _get("AZURE_OPENAI_ENDPOINT", required=True)
AZURE_OPENAI_DEPLOYMENT  = _get("AZURE_OPENAI_DEPLOYMENT", required=True)
AZURE_OPENAI_API_KEY     = _get("AZURE_OPENAI_API_KEY", required=True)
AZURE_OPENAI_API_VERSION = _get("AZURE_OPENAI_API_VERSION", required=True)

# Hiperparâmetros do modelo
MAX_TOKENS  = _get("MAX_TOKENS", 800, cast=int)
TEMPERATURE = _get("TEMPERATURE", 0.2, cast=float)

CROPS_PREFIX = _get("CROPS_PREFIX", "crops", cast=str)
# -------------------------------------------------------------------------
# 🔷 Azure Storage
# -------------------------------------------------------------------------
AZURE_STORAGE_CONNECTION_STRING = _get("AZURE_STORAGE_CONNECTION_STRING", required=True)
BLOB_CONTAINER                  = _get("BLOB_CONTAINER", required=True)

# nova variável separada — usada apenas para gerar SAS
AZURE_STORAGE_ACCOUNT_KEY       = _get("AZURE_STORAGE_KEY", "")

# performance / upload
UPLOAD_MAX_CONCURRENCY = _get("UPLOAD_MAX_CONCURRENCY", 8, cast=int)
SAS_TTL_MINUTES        = _get("SAS_TTL_MINUTES", 30, cast=int)

# prefixo dos crops (pasta no container)
CROPS_PREFIX = _get("CROPS_PREFIX", "crops")

# JSON de ROIs (opcional: blob path)
ROI_JSON_BLOB = _get("ROI_JSON_BLOB", "")


# -------------------------------------------------------------------------
# 🔷 Controle de lotes / retries (para contornar rate limits)
# -------------------------------------------------------------------------
OAI_ROI_BATCH    = _get("OAI_ROI_BATCH", 4, cast=int)      # nº de ROIs por pedido
OAI_MAX_RETRIES  = _get("OAI_MAX_RETRIES", 6, cast=int)    # nº de tentativas
OAI_BACKOFF_BASE = _get("OAI_BACKOFF_BASE", 1.8, cast=float)  # fator de backoff exponencial
