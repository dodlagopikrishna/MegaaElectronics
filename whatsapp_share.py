"""WhatsApp sharing via wa.me deep links."""

import os
import subprocess
import sys
import urllib.parse
import webbrowser

from country_phone_codes import parse_phone
from pdf_generator import generate_transaction_pdf
from store_config import STORE_NAME, STORE_PHONE_DISPLAY


def phone_to_wa_digits(phone: str) -> str:
    """Convert stored phone (+91 7780601679) to wa.me digits (917780601679)."""
    phone = (phone or "").strip()
    if not phone:
        return ""
    code, local = parse_phone(phone)
    return "".join(c for c in f"{code}{local}" if c.isdigit())


def open_whatsapp(message: str, phone: str | None = None) -> None:
    """Open WhatsApp with an optional recipient and pre-filled message."""
    encoded = urllib.parse.quote(message, safe="")
    digits = phone_to_wa_digits(phone) if phone else ""
    url = f"https://wa.me/{digits}?text={encoded}" if digits else f"https://wa.me/?text={encoded}"
    if sys.platform == "darwin":
        subprocess.Popen(["open", url])
    elif sys.platform == "win32":
        os.startfile(url)
    else:
        webbrowser.open(url)


def reveal_file(path: str) -> None:
    """Reveal a file in the system file manager for easy attachment."""
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-R", path])
    elif sys.platform == "win32":
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    else:
        subprocess.Popen(["xdg-open", os.path.dirname(path)])


def format_client_details(client: dict) -> str:
    """Format client record as a WhatsApp message."""
    return "\n".join(
        [
            f"*{STORE_NAME} — Client Details*",
            "",
            f"*Name:* {client.get('name') or '—'}",
            f"*Phone:* {client.get('phone') or '—'}",
            f"*Email:* {client.get('email') or '—'}",
            f"*Address:* {client.get('address') or '—'}",
        ]
    )


def share_client_via_whatsapp(client: dict) -> None:
    """Share client details on WhatsApp, opening the client's chat when possible."""
    open_whatsapp(format_client_details(client), client.get("phone"))


def _transaction_doc_label(tx: dict) -> tuple[str, str]:
    doc_type = tx.get("type", "Estimate")
    if doc_type == "Invoice":
        return "invoice", "INV"
    return "estimate", "EST"


def format_transaction_share_message(tx: dict) -> str:
    """Build a WhatsApp message for an estimate or invoice."""
    doc_label, prefix = _transaction_doc_label(tx)
    client = tx.get("client_name") or "Walk-in"
    greeting = f"Hello {client}," if client != "Walk-in" else "Hello,"
    return "\n".join(
        [
            greeting,
            "",
            f"Please find attached your {doc_label} *{prefix}-{tx['id']:04d}* "
            f"from *{STORE_NAME}*.",
            "",
            f"*Amount:* ₹{tx['total_amount']:,.2f}",
            f"*Date:* {tx['date']}",
            "",
            f"For any queries, contact us at {STORE_PHONE_DISPLAY}.",
            "",
            "Thank you!",
        ]
    )


def share_transaction_pdf_via_whatsapp(tx: dict, items: list) -> str:
    """Generate a transaction PDF, open WhatsApp, and reveal the file for attachment."""
    path = generate_transaction_pdf(tx, items)
    open_whatsapp(format_transaction_share_message(tx), tx.get("client_phone"))
    reveal_file(path)
    return path
