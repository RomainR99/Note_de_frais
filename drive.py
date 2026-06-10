import os
from datetime import datetime

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

from google_credentials import get_google_credentials


class GoogleDriveClient:
    def __init__(self):
        load_dotenv()

        scopes = [
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = get_google_credentials(scopes)
        self.service = build("drive", "v3", credentials=credentials)
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
        self.folder_id = folder_id or None
    def can_upload(self) -> bool:
        return self.folder_id is not None

    def _get_upload_folder_id(self) -> str:
        if not self.folder_id:
            raise ValueError("Aucun dossier Drive configuré pour l'upload.")
        return self.folder_id

    def upload_image(self, image_bytes: bytes, mime_type: str) -> str:
        extension = "jpg" if mime_type == "image/jpeg" else "png"
        filename = f"note-de-frais-{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"

        file_metadata = {
            "name": filename,
            "parents": [self._get_upload_folder_id()],
        }

        media = MediaInMemoryUpload(image_bytes, mimetype=mime_type, resumable=True)

        file = (
            self.service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )

        self.service.permissions().create(
            fileId=file["id"],
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True,
        ).execute()

        return file.get("webViewLink") or f"https://drive.google.com/file/d/{file['id']}/view"
