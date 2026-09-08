"""Append household expense rows into markdown documents."""

from __future__ import annotations

import re
from pathlib import Path

from shared.config import get_documents_dir

# category_id -> (filename, section heading under which the first markdown table lives)
CATEGORY_TARGETS: dict[str, tuple[str, str]] = {
    "home_loan": ("home-loan.md", "## Recent payments"),
    "credit_card": ("credit-cards.md", "## September 2026 bills"),
    "gas": ("utilities.md", "## Gas bill (LPG / PNG)"),
    "electricity": ("utilities.md", "## Electricity bill"),
    "car_maintenance": ("vehicles.md", "## Car maintenance"),
    "bike_maintenance": ("vehicles.md", "## Bike maintenance"),
    "petrol": ("vehicles.md", "## Petrol / fuel (September 2026)"),
    "insurance": ("insurance.md", "## Payments"),
    "medical": ("medical.md", "## September 2026"),
    "daily": ("daily-expenses.md", "## Optional detailed log (add rows anytime)"),
}

CATEGORY_LABELS = {
    "home_loan": "Home loan EMI",
    "credit_card": "Credit card bill",
    "gas": "Gas bill",
    "electricity": "Electricity bill",
    "car_maintenance": "Car maintenance",
    "bike_maintenance": "Bike maintenance",
    "petrol": "Petrol / fuel",
    "insurance": "Insurance payment",
    "medical": "Hospital / medical",
    "daily": "Daily expense",
}


def _format_inr(amount: float | int) -> str:
    n = int(round(float(amount)))
    return f"{n:,}"


def build_row(category: str, data: dict) -> list[str]:
    """Build table cells for the target markdown table."""
    notes = (data.get("notes") or "").replace("|", "/")
    if category == "home_loan":
        return [
            data["month"],
            _format_inr(data["amount"]),
            data.get("principal") or "—",
            data.get("interest") or "—",
            notes or "Added via form",
        ]
    if category == "credit_card":
        return [
            data.get("card") or "Card",
            _format_inr(data["amount"]),
            data.get("minimum_due") or "—",
            data.get("paid") or "Pending",
            notes or "Added via form",
        ]
    if category == "gas":
        return [
            data["month"],
            _format_inr(data["amount"]),
            data.get("due_date") or "—",
            data.get("paid") or "Pending",
            data.get("provider") or "—",
            notes or "Added via form",
        ]
    if category == "electricity":
        return [
            data["month"],
            str(data.get("units") or "—"),
            _format_inr(data["amount"]),
            data.get("due_date") or "—",
            data.get("paid") or "Pending",
            data.get("provider") or "—",
            notes or "Added via form",
        ]
    if category in ("car_maintenance", "bike_maintenance"):
        return [
            data.get("date") or data.get("month") or "—",
            data.get("item") or "Service",
            _format_inr(data["amount"]),
            notes or "Added via form",
        ]
    if category == "petrol":
        return [
            data.get("date") or "—",
            data.get("vehicle") or "Car",
            str(data.get("litres") or "—"),
            _format_inr(data["amount"]),
            notes or "Added via form",
        ]
    if category == "insurance":
        return [
            data.get("date") or "—",
            data.get("policy") or "Policy",
            _format_inr(data["amount"]),
            data.get("paid_via") or "—",
            notes or "Added via form",
        ]
    if category == "medical":
        return [
            data.get("date") or "—",
            data.get("type") or "Expense",
            data.get("who") or "Family",
            _format_inr(data["amount"]),
            data.get("paid_via") or "—",
            notes or "Added via form",
        ]
    if category == "daily":
        return [
            data.get("date") or "—",
            data.get("item") or "Expense",
            _format_inr(data["amount"]),
            notes or "Added via form",
        ]
    raise ValueError(f"Unknown category: {category}")


def _insert_row_after_header(text: str, section_heading: str, cells: list[str]) -> str:
    lines = text.splitlines(keepends=True)
    section_idx = None
    for i, line in enumerate(lines):
        if line.strip() == section_heading.strip():
            section_idx = i
            break
    if section_idx is None:
        raise ValueError(f"Section not found: {section_heading}")

    # Find markdown table header separator (|---|) after the section
    sep_idx = None
    for i in range(section_idx + 1, len(lines)):
        if lines[i].startswith("#"):
            break
        if re.match(r"^\|[\s\-:|]+\|\s*$", lines[i]):
            sep_idx = i
            break
    if sep_idx is None:
        raise ValueError(f"No markdown table under {section_heading}")

    row = "| " + " | ".join(cells) + " |\n"
    # Newest first: insert immediately after separator
    lines.insert(sep_idx + 1, row)
    return "".join(lines)


def append_expense(org_id: str, category: str, data: dict) -> Path:
    if org_id != "household":
        raise ValueError("Expense form currently supports only the household org")
    if category not in CATEGORY_TARGETS:
        raise ValueError(f"Unknown category: {category}")

    filename, section = CATEGORY_TARGETS[category]
    path = get_documents_dir(org_id) / filename
    if not path.exists():
        raise FileNotFoundError(path)

    cells = build_row(category, data)
    updated = _insert_row_after_header(path.read_text(encoding="utf-8"), section, cells)
    path.write_text(updated, encoding="utf-8")
    return path
