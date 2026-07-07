import uuid
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


def save_kyc_document(user_id: uuid.UUID, filename: str, content: bytes) -> str:
    """Local filesystem storage for KYC documents in dev/sandbox.

    Swappable for an S3-compatible backend later — callers only depend on this
    function's signature, never on the filesystem directly.
    """
    directory = Path(settings.kyc_storage_path) / str(user_id)
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{Path(filename).name}"
    path = directory / safe_name
    path.write_bytes(content)
    return str(path)
