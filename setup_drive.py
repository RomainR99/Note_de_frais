import os
import sys

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_credentials import get_google_credentials, get_service_account_email


def validate_folder(folder_id: str) -> None:
    credentials = get_google_credentials(["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=credentials)

    metadata = (
        service.files()
        .get(
            fileId=folder_id,
            fields="id,name,mimeType",
            supportsAllDrives=True,
        )
        .execute()
    )

    if metadata.get("mimeType") != "application/vnd.google-apps.folder":
        raise ValueError(f"L'ID fourni ne correspond pas à un dossier : {metadata.get('name')}")


def update_env(folder_id: str) -> None:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    with open(env_path, encoding="utf-8") as file:
        lines = file.read().splitlines()

    key = "GOOGLE_DRIVE_FOLDER_ID"
    updated = False
    new_lines = []

    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f'{key}="{folder_id}"')
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f'{key}="{folder_id}"')

    with open(env_path, "w", encoding="utf-8") as file:
        file.write("\n".join(new_lines) + "\n")


def print_instructions() -> None:
    email = get_service_account_email()
    print("Configuration du dossier Google Drive pour les images\n")
    print("1. Ouvrez Google Drive")
    print("2. Créez un dossier, par ex. : Justificatifs notes de frais")
    print("3. Clic droit sur le dossier → Partager")
    print(f"4. Ajoutez cet email en Éditeur :\n   {email}")
    print("5. Copiez l'ID du dossier depuis l'URL :")
    print("   https://drive.google.com/drive/folders/ID_A_COPIER_ICI")
    print("\nPuis lancez :")
    print("   python setup_drive.py ID_A_COPIER_ICI")


if __name__ == "__main__":
    load_dotenv()

    if len(sys.argv) < 2:
        print_instructions()
        sys.exit(1)

    folder_id = sys.argv[1].strip()

    if folder_id in {"ID_ICI", "ID_A_COPIER_ICI", "votre_id_de_dossier"}:
        print("Erreur : remplacez ID_ICI par le vrai ID du dossier Drive.")
        print_instructions()
        sys.exit(1)

    try:
        validate_folder(folder_id)
        update_env(folder_id)
        print(f"Dossier Drive validé et enregistré dans .env : {folder_id}")
        print("Relancez uvicorn puis réessayez l'envoi.")
    except HttpError as exc:
        print("Accès refusé au dossier.")
        print("Vérifiez que le dossier est bien partagé avec le compte de service.")
        print_instructions()
        sys.exit(1)
    except Exception as exc:
        print(f"Erreur : {exc}")
        sys.exit(1)
