# app/blob_io.py

from __future__ import annotations
import mimetypes
from datetime import datetime, timedelta
from typing import Iterable, List, Tuple

from azure.storage.blob import (
    BlobServiceClient,
    BlobSasPermissions,
    generate_blob_sas,
)

from .env import (
    AZURE_STORAGE_CONNECTION_STRING,
    BLOB_CONTAINER,
    AZURE_STORAGE_ACCOUNT_KEY,
    CROPS_PREFIX,
)

# -------------------------------------------------------------------------
# Ligação ao Blob
# -------------------------------------------------------------------------
blob_service = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)
container_client = blob_service.get_container_client(BLOB_CONTAINER)

# -------------------------------------------------------------------------
# Listar imagens originais (exclui crops/)
# -------------------------------------------------------------------------
def list_all_images(exclude_prefix: str | None = None) -> List[str]:
    """
    Lista todos os blobs de imagem no container, excluindo tudo o que estiver
    dentro do prefixo de crops (por defeito: CROPS_PREFIX + '/').
    """
    ex_prefix = (exclude_prefix or (CROPS_PREFIX + "/")).lower()

    names: List[str] = []
    for blob in container_client.list_blobs():
        name = blob.name
        lname = name.lower()

        # ignora o que está dentro de crops/
        if lname.startswith(ex_prefix):
            continue

        if lname.endswith((".jpg", ".jpeg", ".png", ".webp")):
            names.append(name)

    return names

# -------------------------------------------------------------------------
# Download helpers
# -------------------------------------------------------------------------
def read_blob_bytes(blob_name: str) -> bytes:
    """
    Lê um blob arbitrário e devolve os bytes.
    """
    bc = container_client.get_blob_client(blob_name)
    return bc.download_blob().readall()

def download_image(blob_name: str) -> Tuple[bytes, str]:
    """
    Faz download de uma imagem e devolve (bytes, mime_type).
    """
    data = read_blob_bytes(blob_name)
    mime, _ = mimetypes.guess_type(blob_name)
    if not mime:
        mime = "image/jpeg"
    return data, mime

# -------------------------------------------------------------------------
# Upload helpers
# -------------------------------------------------------------------------
def upload_bytes_many(
    items: Iterable[Tuple[str, bytes, str]]
) -> List[str]:
    """
    Faz upload de vários blobs de uma vez.
    items = [(blob_path, bytes_data, content_type), ...]
    Devolve lista de paths efectivamente enviados.
    """
    uploaded: List[str] = []
    for path, data, content_type in items:
        bc = container_client.get_blob_client(path)
        bc.upload_blob(data, overwrite=True, content_type=content_type)
        uploaded.append(path)
    return uploaded

# -------------------------------------------------------------------------
# SAS helpers
# -------------------------------------------------------------------------
def make_sas_url(blob_path: str, minutes: int = 60) -> str:
    """
    Cria um SAS URL de leitura para um blob específico.
    Requer AZURE_STORAGE_ACCOUNT_KEY definido no .env/env.py.
    """
    # nome da conta vem da connection string
    account_name = blob_service.account_name

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=BLOB_CONTAINER,
        blob_name=blob_path,
        account_key=AZURE_STORAGE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(minutes=minutes),
    )

    # construir URL final
    blob_client = container_client.get_blob_client(blob_path)
    return f"{blob_client.url}?{sas_token}"

