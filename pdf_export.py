import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from dashboard import compute_monthly_stats, filter_expenses_by_month, parse_amount

MONTH_NAMES = [
    "",
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]


def _cell(value) -> str:
    if value is None or value == "":
        return "—"
    return str(value)


def generate_monthly_pdf(expenses: list[dict], year: int, month: int) -> bytes:
    month_expenses = filter_expenses_by_month(expenses, year, month)
    stats = compute_monthly_stats(expenses, year, month)
    month_label = f"{MONTH_NAMES[month]} {year}"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=8,
    )

    story = [
        Paragraph("Récapitulatif mensuel — Notes de frais", title_style),
        Paragraph(
            f"Période : {month_label} — Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            subtitle_style,
        ),
    ]

    summary_data = [
        ["Dépenses mensuelles", f"{stats['total_ttc']:.2f} €"],
        ["TVA mensuelle", f"{stats['total_tva']:.2f} €"],
        ["Nombre de notes", str(stats["count"])],
    ]
    summary_table = Table(summary_data, colWidths=[8 * cm, 8 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f6fa")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)

    story.append(Paragraph("Dépenses par employé", section_style))
    if stats["employees"]:
        employee_data = [["Employé", "Notes", "Total TTC", "Total TVA"]]
        for employee in stats["employees"]:
            employee_data.append(
                [
                    employee["employe"],
                    str(employee["count"]),
                    f"{employee['montant_ttc']:.2f} €",
                    f"{employee['tva']:.2f} €",
                ]
            )
        employee_table = Table(
            employee_data,
            colWidths=[6 * cm, 2.5 * cm, 4 * cm, 4 * cm],
            repeatRows=1,
        )
        employee_table.setStyle(_table_style())
        story.append(employee_table)
    else:
        story.append(Paragraph("Aucune dépense pour ce mois.", styles["Normal"]))

    story.append(Paragraph("Détail des notes de frais", section_style))
    if month_expenses:
        detail_data = [
            [
                "Date",
                "Employé",
                "Type",
                "Fournisseur",
                "TTC",
                "TVA",
                "Devise",
            ]
        ]
        for expense in month_expenses:
            detail_data.append(
                [
                    _cell(expense.get("date")),
                    _cell(expense.get("employe") or "Non renseigné"),
                    _cell(expense.get("type_document")),
                    _cell(expense.get("fournisseur")),
                    f"{parse_amount(expense.get('montant_ttc')):.2f}",
                    f"{parse_amount(expense.get('tva')):.2f}",
                    _cell(expense.get("devise") or "EUR"),
                ]
            )
        detail_table = Table(
            detail_data,
            colWidths=[2.2 * cm, 3 * cm, 2.5 * cm, 4 * cm, 2 * cm, 2 * cm, 1.8 * cm],
            repeatRows=1,
        )
        detail_table.setStyle(_table_style())
        story.append(detail_table)
    else:
        story.append(Paragraph("Aucune note de frais pour cette période.", styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e3345")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
    )
