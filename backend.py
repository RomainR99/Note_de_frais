import os
import json
import base64
from dotenv import load_dotenv
from groq import Groq


class ExpenseAgent:
    def __init__(self):
        load_dotenv()

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        base_dir = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(base_dir, "context.txt"), "r", encoding="utf-8") as f:
            self.context = f.read()

        with open(os.path.join(base_dir, "prompt.txt"), "r", encoding="utf-8") as f:
            self.prompt = f.read()

        self.expected_fields = {
            "type_document": None, #gere erreur si le json ne retourne rien
            "fournisseur": None,
            "date": None,
            "montant_ttc": None,
            "tva": None,
            "devise": "EUR",
            "description": None,
            "confiance": None,
        }

    def extract_from_bytes(self, image_bytes, media_type):
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        response = self.client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": self.context,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": self.prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_base64}"
                            },
                        },
                    ],
                },
            ],
        )

        content = response.choices[0].message.content

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {}

        result = self.expected_fields.copy()

        for field in self.expected_fields:
            if field in data:
                result[field] = data[field]

        return result

if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_dir, "receipts", "1000-receipt.jpg")

    with open(image_path, "rb") as file:
        image_bytes = file.read()

    agent = ExpenseAgent()

    result = agent.extract_from_bytes(
        image_bytes=image_bytes,
        media_type="image/jpeg"
    )

    print(result)