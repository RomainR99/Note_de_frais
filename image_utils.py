import os
from datetime import datetime
from uuid import uuid4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")


def save_image(image_bytes: bytes, mime_type: str, base_url: str) -> str:
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    extension = "jpg" if mime_type == "image/jpeg" else "png"
    filename = (
        f"note-de-frais-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        f"-{uuid4().hex[:8]}.{extension}"
    )

    filepath = os.path.join(UPLOADS_DIR, filename)
    with open(filepath, "wb") as file:
        file.write(image_bytes)

    return f"{base_url.rstrip('/')}/uploads/{filename}"
