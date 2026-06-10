import json
import os

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_credentials_info() -> dict:
    load_dotenv()

    env_json = os.getenv("GOOGLE_CREDENTIALS") or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if env_json:
        return json.loads(env_json)

    credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    paths = [
        os.path.join(BASE_DIR, credentials_file),
        "/app/credentials.json",
    ]

    for path in paths:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as file:
                return json.load(file)

    raise ValueError(
        "Credentials Google introuvables. "
        "Définissez GOOGLE_CREDENTIALS (variable d'environnement) "
        "ou placez credentials.json en local."
    )


def get_google_credentials(scopes: list[str]) -> Credentials:
    return Credentials.from_service_account_info(
        load_credentials_info(),
        scopes=scopes,
    )


def get_service_account_email() -> str:
    return load_credentials_info()["client_email"]
