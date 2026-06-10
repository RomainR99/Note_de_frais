from collections import defaultdict
from datetime import datetime


def parse_amount(value) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return 0.0


def parse_expense_date(date_str: str) -> datetime | None:
    if not date_str:
        return None

    for fmt in ("%d/%m/%Y", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    return None


def get_expense_month(expense: dict) -> tuple[int, int] | None:
    parsed = parse_expense_date(expense.get("date"))
    if parsed:
        return parsed.year, parsed.month

    parsed = parse_expense_date(expense.get("horodatage"))
    if parsed:
        return parsed.year, parsed.month

    return None


def compute_monthly_stats(expenses: list[dict], year: int, month: int) -> dict:
    total_ttc = 0.0
    total_tva = 0.0
    by_employee: dict[str, dict[str, float]] = defaultdict(
        lambda: {"montant_ttc": 0.0, "tva": 0.0, "count": 0}
    )

    for expense in expenses:
        expense_month = get_expense_month(expense)
        if expense_month != (year, month):
            continue

        montant = parse_amount(expense.get("montant_ttc"))
        tva = parse_amount(expense.get("tva"))
        employee = (expense.get("employe") or "").strip() or "Non renseigné"

        total_ttc += montant
        total_tva += tva
        by_employee[employee]["montant_ttc"] += montant
        by_employee[employee]["tva"] += tva
        by_employee[employee]["count"] += 1

    employees = [
        {
            "employe": name,
            "montant_ttc": round(stats["montant_ttc"], 2),
            "tva": round(stats["tva"], 2),
            "count": int(stats["count"]),
        }
        for name, stats in sorted(
            by_employee.items(),
            key=lambda item: item[1]["montant_ttc"],
            reverse=True,
        )
    ]

    return {
        "year": year,
        "month": month,
        "total_ttc": round(total_ttc, 2),
        "total_tva": round(total_tva, 2),
        "count": sum(employee["count"] for employee in employees),
        "employees": employees,
    }


def resolve_month(expenses: list[dict], selected_month: str) -> tuple[int, int]:
    months = available_months(expenses)
    now = datetime.now()

    if selected_month:
        year_str, month_str = selected_month.split("-")
        return int(year_str), int(month_str)
    if months:
        return months[0]
    return now.year, now.month


def filter_expenses_by_month(
    expenses: list[dict], year: int, month: int
) -> list[dict]:
    return [
        expense
        for expense in expenses
        if get_expense_month(expense) == (year, month)
    ]


def available_months(expenses: list[dict]) -> list[tuple[int, int]]:
    months = set()
    for expense in expenses:
        expense_month = get_expense_month(expense)
        if expense_month:
            months.add(expense_month)

    return sorted(months, reverse=True)
