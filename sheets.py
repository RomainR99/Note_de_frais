import os
from datetime import datetime
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsClient:
    def __init__(self):
        load_dotenv()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        credentials_path = os.path.join(base_dir, credentials_file)

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=scopes,
        )

        self.client = gspread.authorize(credentials)

        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        sheet_name = os.getenv("GOOGLE_SHEET_NAME", "Notes de frais")

        self.sheet = self.client.open_by_key(sheet_id)
        self.worksheet = self.sheet.worksheet(sheet_name)

    def append_expense(self, data: dict, image_url: str = None):
        row = [
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            data.get("type_document"),
            data.get("fournisseur"),
            data.get("date"),
            data.get("montant_ttc"),
            data.get("tva"),
            data.get("devise", "EUR"),
            data.get("description"),
            data.get("confiance"),
            image_url,
        ]

        self.worksheet.append_row(row, value_input_option="USER_ENTERED")

        return row


if __name__ == "__main__":
    sheets_client = GoogleSheetsClient()

    fake_data = {
        "type_document": "restaurant",
        "fournisseur": "Bistrot Paul",
        "date": "08/06/2026",
        "montant_ttc": 24.90,
        "tva": 2.49,
        "devise": "EUR",
        "description": "Repas professionnel",
        "confiance": 95,
    }

    result = sheets_client.append_expense(fake_data)

    print("Ligne ajoutée dans Google Sheets :")
    print(result)