from fpdf import FPDF
from datetime import datetime
import os
import sys

from PIL import Image

from app_config import get_export_dir
from store_config import (
    STORE_ADDRESS,
    STORE_CITY,
    STORE_GSTIN,
    STORE_LOGO_FILENAME,
    STORE_NAME,
    STORE_PHONE_DISPLAY,
    STORE_TAGLINE,
)


def _resolve_base_dir():
    """Return the directory containing bundled data (assets, default exports)."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _resolve_output_dir():
    configured = get_export_dir()
    if configured:
        return configured
    return os.path.join(_resolve_base_dir(), "exports")


OUTPUT_DIR = _resolve_output_dir()
ASSETS_DIR = os.path.join(_resolve_base_dir(), "assets")
PDF_LOGO_CACHE = os.path.join(ASSETS_DIR, "megaa_electronics_logo_pdf.png")

MARGIN = 15
HEADER_HEIGHT = 46
LOGO_HEIGHT_MM = 32


def _get_logo_path():
    path = os.path.join(ASSETS_DIR, STORE_LOGO_FILENAME)
    return path if os.path.isfile(path) else None


def _prepare_logo_for_pdf():
    """Crop transparent padding and resize for crisp, lightweight PDF embedding."""
    source = _get_logo_path()
    if not source:
        return None

    source_mtime = os.path.getmtime(source)
    if os.path.isfile(PDF_LOGO_CACHE) and os.path.getmtime(PDF_LOGO_CACHE) >= source_mtime:
        return PDF_LOGO_CACHE

    img = Image.open(source).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    target_h = 480
    scale = target_h / img.height
    resized = img.resize((int(img.width * scale), target_h), Image.LANCZOS)
    resized.save(PDF_LOGO_CACHE, "PNG", optimize=True)
    return PDF_LOGO_CACHE


def _format_date(date_str):
    if not date_str:
        return datetime.now().strftime("%d %b %Y")
    try:
        return datetime.strptime(str(date_str)[:10], "%Y-%m-%d").strftime("%d %b %Y")
    except ValueError:
        return str(date_str)


def _display_client_name(transaction):
    name = transaction.get("client_name")
    if name and str(name).strip().lower() not in ("none", ""):
        return str(name).strip()
    return "Walk-in Customer"


class MEGAAPdf(FPDF):
    """Custom PDF class with MEGAA Electronics branding."""

    BRAND_COLOR = (41, 128, 185)
    DARK_TEXT = (44, 62, 80)
    MUTED_TEXT = (90, 98, 104)
    LIGHT_BG = (245, 247, 250)
    ACCENT = (39, 174, 96)
    BORDER = (210, 214, 220)

    def __init__(self, doc_type="Estimate"):
        super().__init__()
        self.doc_type = doc_type
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(MARGIN, HEADER_HEIGHT + 8, MARGIN)

    def header(self):
        self.set_fill_color(255, 255, 255)
        self.rect(0, 0, 210, HEADER_HEIGHT, "F")

        logo_path = _prepare_logo_for_pdf()
        text_x = MARGIN
        content_y = 7

        if logo_path:
            logo_info = self.image(logo_path, x=MARGIN, y=content_y, h=LOGO_HEIGHT_MM)
            text_x = MARGIN + logo_info.rendered_width + 8

        badge_w = 40
        badge_x = 210 - MARGIN - badge_w
        text_width = badge_x - text_x - 4

        self.set_font("Helvetica", "B", 17)
        self.set_text_color(*self.BRAND_COLOR)
        self.set_xy(text_x, content_y)
        self.cell(text_width, 7, STORE_NAME, ln=True)

        self.set_fill_color(*self.BRAND_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.set_xy(badge_x, content_y)
        self.cell(badge_w, 9, self.doc_type.upper(), align="C", fill=True)

        self.set_text_color(*self.MUTED_TEXT)
        self.set_font("Helvetica", "", 7)
        self.set_xy(text_x, content_y + 9)
        self.multi_cell(text_width, 3.5, STORE_TAGLINE)

        details_y = max(self.get_y() + 1, content_y + 22)
        self.set_xy(text_x, details_y)
        self.cell(
            text_width,
            3.5,
            f"Tel: {STORE_PHONE_DISPLAY}   |   GSTIN: {STORE_GSTIN}",
            ln=True,
        )
        self.set_x(text_x)
        self.cell(text_width, 3.5, STORE_ADDRESS, ln=True)

        self.set_draw_color(*self.BRAND_COLOR)
        self.set_line_width(0.6)
        self.line(MARGIN, HEADER_HEIGHT - 1.5, 210 - MARGIN, HEADER_HEIGHT - 1.5)

        self.set_y(HEADER_HEIGHT + 6)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.MUTED_TEXT)
        self.set_draw_color(*self.BORDER)
        self.line(MARGIN, self.get_y(), 210 - MARGIN, self.get_y())
        self.ln(2)
        self.cell(
            0,
            4,
            f"{STORE_NAME}  |  {STORE_CITY}  |  Tel: {STORE_PHONE_DISPLAY}  |  GSTIN: {STORE_GSTIN}",
            align="L",
            ln=True,
        )
        self.cell(
            0,
            4,
            f"Generated {datetime.now().strftime('%d %b %Y %H:%M')}",
            align="L",
        )
        self.cell(0, 4, f"Page {self.page_no()}/{{nb}}", align="R")

    def _draw_meta_box(self, x, y, width, rows):
        row_h = 6
        box_h = row_h * len(rows) + 4
        self.set_draw_color(*self.BORDER)
        self.set_fill_color(*self.LIGHT_BG)
        self.rect(x, y, width, box_h, "DF")

        inner_y = y + 2
        for row in rows:
            label, value = row[0], row[1]
            bold = row[2] if len(row) > 2 else False
            value_color = row[3] if len(row) > 3 else self.DARK_TEXT

            self.set_xy(x + 3, inner_y)
            self.set_font("Helvetica", "B" if bold else "", 9)
            self.set_text_color(*self.DARK_TEXT)
            label_text = f"{label}: "
            self.cell(self.get_string_width(label_text) + 1, row_h, label_text, ln=False)
            self.set_text_color(*value_color)
            self.cell(width - 6 - self.get_string_width(label_text), row_h, str(value), ln=True)
            inner_y += row_h

        return box_h


def generate_transaction_pdf(transaction, items, save_path=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc_type = transaction.get("type", "Estimate")
    pdf = MEGAAPdf(doc_type=doc_type)
    pdf.alias_nb_pages()
    pdf.add_page()

    doc_date = _format_date(transaction.get("date"))
    status = transaction.get("status", "Pending")

    meta_y = pdf.get_y()
    left_box_w = 88
    right_box_w = 88
    right_box_x = 210 - MARGIN - right_box_w

    status_color = MEGAAPdf.ACCENT if status == "Paid" else MEGAAPdf.DARK_TEXT
    pdf._draw_meta_box(
        MARGIN,
        meta_y,
        left_box_w,
        [
            (doc_type, f"#{transaction['id']:04d}", True),
            ("Status", status, True, status_color),
        ],
    )

    pdf._draw_meta_box(
        right_box_x,
        meta_y,
        right_box_w,
        [
            ("Date", doc_date, False),
            ("Prepared by", STORE_NAME, False),
        ],
    )

    pdf.set_y(meta_y + 18)

    client_name = _display_client_name(transaction)
    bill_box_y = pdf.get_y()
    bill_box_h = 24
    extra_lines = sum(
        1
        for key in ("client_address", "client_phone", "client_email")
        if transaction.get(key)
    )
    bill_box_h += extra_lines * 5

    pdf.set_draw_color(*MEGAAPdf.BORDER)
    pdf.set_fill_color(*MEGAAPdf.LIGHT_BG)
    pdf.rect(MARGIN, bill_box_y, 180, bill_box_h, "DF")

    pdf.set_xy(MARGIN + 3, bill_box_y + 2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*MEGAAPdf.DARK_TEXT)
    pdf.cell(0, 6, "Bill To", ln=True)

    pdf.set_x(MARGIN + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, client_name, ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*MEGAAPdf.MUTED_TEXT)
    if transaction.get("client_address"):
        pdf.set_x(MARGIN + 3)
        pdf.cell(0, 5, transaction["client_address"], ln=True)
    if transaction.get("client_phone"):
        pdf.set_x(MARGIN + 3)
        pdf.cell(0, 5, f"Tel: {transaction['client_phone']}", ln=True)
    if transaction.get("client_email"):
        pdf.set_x(MARGIN + 3)
        pdf.cell(0, 5, f"Email: {transaction['client_email']}", ln=True)

    pdf.set_y(bill_box_y + bill_box_h + 6)

    col_widths = [10, 58, 28, 16, 28, 30]
    headers = ["#", "Item", "Description", "Qty", "Unit Price", "Total"]
    table_width = sum(col_widths)

    pdf.set_fill_color(*MEGAAPdf.BRAND_COLOR)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_x(MARGIN)

    for i, header in enumerate(headers):
        align = "R" if i >= 3 else "L"
        pdf.cell(col_widths[i], 8, header, fill=True, align=align, border=0)
    pdf.ln()

    pdf.set_text_color(*MEGAAPdf.DARK_TEXT)
    pdf.set_font("Helvetica", "", 9)
    row_fill = False

    for idx, item in enumerate(items, 1):
        pdf.set_x(MARGIN)
        pdf.set_fill_color(*(MEGAAPdf.LIGHT_BG if row_fill else (255, 255, 255)))

        pdf.cell(col_widths[0], 7, str(idx), fill=True, border="B")
        pdf.cell(col_widths[1], 7, str(item.get("item_name", ""))[:38], fill=True, border="B")
        pdf.cell(col_widths[2], 7, str(item.get("description", ""))[:18], fill=True, border="B")
        pdf.cell(col_widths[3], 7, str(item.get("quantity", 1)), fill=True, align="R", border="B")
        pdf.cell(
            col_widths[4],
            7,
            f"Rs.{item.get('unit_price', 0):,.2f}",
            fill=True,
            align="R",
            border="B",
        )
        pdf.cell(
            col_widths[5],
            7,
            f"Rs.{item.get('total_price', 0):,.2f}",
            fill=True,
            align="R",
            border="B",
        )
        pdf.ln()

        row_fill = not row_fill

    pdf.ln(4)
    totals_x = MARGIN + table_width - 58
    val_x = MARGIN + table_width

    pdf.set_font("Helvetica", "", 10)
    pdf.set_draw_color(*MEGAAPdf.BORDER)
    pdf.line(totals_x, pdf.get_y(), val_x, pdf.get_y())
    pdf.ln(2)

    pdf.set_xy(totals_x, pdf.get_y())
    pdf.cell(val_x - totals_x - 30, 6, "Subtotal:")
    pdf.cell(30, 6, f"Rs.{transaction.get('subtotal', 0):,.2f}", align="R", ln=True)

    if transaction.get("discount_amount", 0) > 0 or transaction.get("discount_percent", 0) > 0:
        dtype = transaction.get("discount_type", "flat")
        if dtype == "flat":
            disc_label = f"Discount (Rs.{transaction['discount_percent']:,.2f} off):"
        else:
            disc_label = f"Discount ({transaction['discount_percent']}%):"
        pdf.set_xy(totals_x, pdf.get_y())
        pdf.cell(val_x - totals_x - 30, 6, disc_label)
        pdf.cell(30, 6, f"-Rs.{transaction.get('discount_amount', 0):,.2f}", align="R", ln=True)

    if transaction.get("tax_enabled") or transaction.get("tax_rate", 0) > 0:
        pdf.set_xy(totals_x, pdf.get_y())
        pdf.cell(val_x - totals_x - 30, 6, f"GST ({transaction['tax_rate']}%):")
        pdf.cell(30, 6, f"Rs.{transaction.get('tax_amount', 0):,.2f}", align="R", ln=True)

    pdf.ln(1)
    pdf.set_xy(totals_x, pdf.get_y())
    pdf.set_fill_color(*MEGAAPdf.BRAND_COLOR)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(val_x - totals_x - 30, 9, "TOTAL:", fill=True)
    pdf.cell(30, 9, f"Rs.{transaction.get('total_amount', 0):,.2f}", fill=True, align="R", ln=True)
    pdf.set_text_color(*MEGAAPdf.DARK_TEXT)

    if transaction.get("notes"):
        pdf.ln(8)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Notes:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*MEGAAPdf.MUTED_TEXT)
        pdf.multi_cell(0, 5, transaction["notes"])
        pdf.set_text_color(*MEGAAPdf.DARK_TEXT)

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, "Terms & Conditions:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MEGAAPdf.MUTED_TEXT)
    if doc_type == "Invoice":
        terms = [
            "1. Payment is due upon receipt unless otherwise agreed in writing.",
            "2. Goods once sold will not be taken back except for manufacturing defects.",
            "3. Warranty: 1 year on hardware, 90 days on installation workmanship.",
        ]
    else:
        terms = [
            "1. This quotation is valid for 1 week from the date of issue.",
            "2. Payment terms: 50% deposit upon confirmation, balance upon completion.",
            "3. Warranty: 1 year on hardware, 90 days on installation workmanship.",
            "4. Prices are subject to change without prior notice.",
        ]
    for term in terms:
        pdf.cell(0, 5, term, ln=True)

    if not save_path:
        safe_name = _display_client_name(transaction).replace(" ", "_")
        filename = f"{doc_type}_{transaction['id']:04d}_{safe_name}.pdf"
        save_path = os.path.join(OUTPUT_DIR, filename)

    pdf.output(save_path)
    return save_path
