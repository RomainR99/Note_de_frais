import base64
import html
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend import ExpenseAgent
from image_utils import save_image
from sheets import GoogleSheetsClient

load_dotenv()

app = FastAPI(title="Note de frais")

base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")
uploads_dir = os.path.join(base_dir, "uploads")

os.makedirs(uploads_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

DOCUMENT_TYPES = ["restaurant", "transport", "hotel", "autre"]


def _escape(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def render_form(data: dict, image_base64: str, media_type: str) -> str:
    type_document = data.get("type_document") or ""
    options = "\n".join(
        f'<option value="{t}"{" selected" if type_document == t else ""}>{t.capitalize()}</option>'
        for t in DOCUMENT_TYPES
    )

    return f"""
<div class="form-card">
  <h2>Résultat de l'analyse</h2>
  <p class="confidence">Confiance : {_escape(data.get("confiance"))}%</p>
  <form
    id="expense-form"
    hx-post="/api/submit"
    hx-target="#confirmation-container"
    hx-swap="innerHTML"
    hx-encoding="multipart/form-data"
  >
    <input type="hidden" name="image_base64" id="image-base64" value="{_escape(image_base64)}">
    <input type="hidden" name="media_type" value="{_escape(media_type)}">
    <input type="hidden" name="confiance" value="{_escape(data.get("confiance"))}">

    <div class="form-grid">
      <label>
        Type de document
        <select name="type_document" required>
          <option value="">— Sélectionner —</option>
          {options}
        </select>
      </label>

      <label>
        Fournisseur
        <input type="text" name="fournisseur" value="{_escape(data.get("fournisseur"))}">
      </label>

      <label>
        Date
        <input type="text" name="date" placeholder="JJ/MM/AAAA" value="{_escape(data.get("date"))}">
      </label>

      <label>
        Montant TTC
        <input type="number" name="montant_ttc" step="0.01" min="0" value="{_escape(data.get("montant_ttc"))}">
      </label>

      <label>
        TVA
        <input type="number" name="tva" step="0.01" min="0" value="{_escape(data.get("tva"))}">
      </label>

      <label>
        Devise
        <input type="text" name="devise" value="{_escape(data.get("devise") or "EUR")}">
      </label>
    </div>

    <label>
      Description
      <textarea name="description" rows="3">{_escape(data.get("description"))}</textarea>
    </label>

    <button type="submit" class="btn btn-primary">Envoyer vers le Google Sheet</button>
  </form>
</div>
"""


def render_expenses_list(expenses: list[dict]) -> str:
    if not expenses:
        return '<p class="empty-state">Aucune note enregistrée pour le moment.</p>'

    rows_html = []
    for expense in expenses:
        image_url = expense.get("image_url") or ""
        has_image = image_url.startswith("http")

        if has_image:
            image_button = (
                f'<button type="button" class="btn btn-small btn-image" '
                f'data-image-url="{_escape(image_url)}">Voir l\'image</button>'
            )
        else:
            image_button = '<span class="text-muted">—</span>'

        rows_html.append(
            f"""
            <tr>
              <td>{_escape(expense.get("horodatage"))}</td>
              <td>{_escape(expense.get("type_document"))}</td>
              <td>{_escape(expense.get("fournisseur"))}</td>
              <td>{_escape(expense.get("date"))}</td>
              <td>{_escape(expense.get("montant_ttc"))} {_escape(expense.get("devise"))}</td>
              <td>{_escape(expense.get("description"))}</td>
              <td>{image_button}</td>
            </tr>
            """
        )

    return f"""
    <div class="table-wrapper">
      <table class="expenses-table">
        <thead>
          <tr>
            <th>Horodatage</th>
            <th>Type</th>
            <th>Fournisseur</th>
            <th>Date</th>
            <th>Montant</th>
            <th>Description</th>
            <th>Image</th>
          </tr>
        </thead>
        <tbody>
          {"".join(rows_html)}
        </tbody>
      </table>
    </div>
    """


def render_confirmation(success: bool, message: str, image_url: str = None) -> str:
    css_class = "alert-success" if success else "alert-error"
    content = html.escape(message)

    if success and image_url:
        content += (
            f'<br>Image : <a href="{html.escape(image_url)}" target="_blank">'
            f"{html.escape(image_url)}</a>"
        )

    return f'<div class="alert {css_class}">{content}</div>'


@app.get("/")
async def index():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/api/expenses", response_class=HTMLResponse)
async def list_expenses():
    try:
        sheets_client = GoogleSheetsClient()
        expenses = sheets_client.list_expenses()
        return render_expenses_list(expenses)
    except Exception as exc:
        return f'<p class="alert alert-error">Impossible de charger les notes : {html.escape(str(exc))}</p>'


@app.post("/api/analyze", response_class=HTMLResponse)
async def analyze(file: UploadFile = File(...)):
    image_bytes = await file.read()
    media_type = file.content_type or "image/jpeg"

    agent = ExpenseAgent()
    result = agent.extract_from_bytes(image_bytes, media_type)

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return render_form(result, image_base64, media_type)


@app.post("/api/submit", response_class=HTMLResponse)
async def submit(
    type_document: str = Form(""),
    fournisseur: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    montant_ttc: Optional[str] = Form(None),
    tva: Optional[str] = Form(None),
    devise: str = Form("EUR"),
    description: Optional[str] = Form(None),
    confiance: Optional[str] = Form(None),
    image_base64: Optional[str] = Form(None),
    media_type: Optional[str] = Form(None),
):
    try:
        data = {
            "type_document": type_document or None,
            "fournisseur": fournisseur or None,
            "date": date or None,
            "montant_ttc": float(montant_ttc) if montant_ttc else None,
            "tva": float(tva) if tva else None,
            "devise": devise or "EUR",
            "description": description or None,
            "confiance": int(confiance) if confiance else None,
        }

        image_url = None
        if image_base64:
            image_bytes = base64.b64decode(image_base64)
            base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
            image_url = save_image(
                image_bytes,
                mime_type=media_type or "image/jpeg",
                base_url=base_url,
            )

        sheets_client = GoogleSheetsClient()
        sheets_client.append_expense(data, image_url=image_url)

        return render_confirmation(
            success=True,
            message="Note de frais envoyée avec succès vers Google Sheets.",
            image_url=image_url,
        )
    except Exception as exc:
        return render_confirmation(
            success=False,
            message=f"Échec de l'envoi : {exc}",
        )
