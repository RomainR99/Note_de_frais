import os
from datetime import datetime

from dotenv import load_dotenv
import gspread

from google_credentials import get_google_credentials


class GoogleSheetsClient:
    def __init__(self):
        load_dotenv()

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = get_google_credentials(scopes)
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

    def list_expenses(self) -> list[dict]:
        rows = self.worksheet.get_all_values()
        if len(rows) <= 1:
            return []

        expenses = []
        for row in reversed(rows[1:]):
            padded = row + [""] * (10 - len(row))
            expenses.append(
                {
                    "horodatage": padded[0],
                    "type_document": padded[1],
                    "fournisseur": padded[2],
                    "date": padded[3],
                    "montant_ttc": padded[4],
                    "tva": padded[5],
                    "devise": padded[6],
                    "description": padded[7],
                    "confiance": padded[8],
                    "image_url": padded[9],
                }
            )

        return expenses


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