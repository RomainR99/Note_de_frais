import os
from datetime import datetime

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload


class GoogleDriveClient:
    def __init__(self):
        load_dotenv()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        credentials_path = os.path.join(base_dir, credentials_file)

        scopes = [
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=scopes,
        )

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
