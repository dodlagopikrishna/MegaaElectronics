from fpdf import FPDF
from datetime import datetime
import os


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")


class MEGAPdf(FPDF):
    """Custom PDF class with MEGA Electronics branding."""

    BRAND_COLOR = (41, 128, 185)
    DARK_TEXT = (44, 62, 80)
    LIGHT_BG = (236, 240, 241)
    ACCENT = (39, 174, 96)

    def __init__(self, doc_type="Estimate"):
        super().__init__()
        self.doc_type = doc_type
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        self.set_fill_color(*self.BRAND_COLOR)
        self.rect(0, 0, 210, 40, "F")

        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.set_xy(15, 8)
        self.cell(0, 10, "MEGA Electronics", ln=False)

        self.set_font("Helvetica", "", 9)
        self.set_xy(15, 20)
        self.cell(0, 5, "CCTV | Projectors | Installation | Maintenance", ln=False)

        self.set_font("Helvetica", "B", 14)
        self.set_xy(-70, 10)
        self.cell(55, 10, self.doc_type.upper(), align="R", ln=False)

        self.set_xy(15, 28)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 5, "Tel: +65 6123 4567  |  info@megaelectronics.sg  |  www.megaelectronics.sg", ln=True)

        self.ln(15)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.DARK_TEXT)
        self.set_draw_color(*self.BRAND_COLOR)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)
        self.cell(0, 5, f"MEGA Electronics  |  Generated {datetime.now().strftime('%d %b %Y %H:%M')}", align="L")
        self.cell(0, 5, f"Page {self.page_no()}/{{nb}}", align="R")


def generate_transaction_pdf(transaction, items, save_path=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc_type = transaction.get("type", "Estimate")
    pdf = MEGAPdf(doc_type=doc_type)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Document info section
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*MEGAPdf.DARK_TEXT)

    info_y = pdf.get_y()
    pdf.set_xy(15, info_y)
    pdf.cell(90, 7, f"{doc_type} #{transaction['id']:04d}", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Date: {transaction.get('date', datetime.now().strftime('%Y-%m-%d'))}", align="R", ln=True)

    status = transaction.get("status", "Pending")
    if status == "Paid":
        pdf.set_text_color(*MEGAPdf.ACCENT)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, f"Status: {status}", ln=True)
    pdf.set_text_color(*MEGAPdf.DARK_TEXT)

    pdf.ln(4)

    # Client info box
    client_name = transaction.get("client_name", "Walk-in Customer")
    pdf.set_fill_color(*MEGAPdf.LIGHT_BG)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "  Bill To:", fill=True, ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"  {client_name}", ln=True)
    if transaction.get("client_address"):
        pdf.cell(0, 6, f"  {transaction['client_address']}", ln=True)
    if transaction.get("client_phone"):
        pdf.cell(0, 6, f"  Tel: {transaction['client_phone']}", ln=True)
    if transaction.get("client_email"):
        pdf.cell(0, 6, f"  Email: {transaction['client_email']}", ln=True)

    pdf.ln(6)

    # Items table header
    col_widths = [10, 52, 25, 16, 30, 30]
    headers = ["#", "Item", "Description", "Qty", "Unit Price", "Total"]

    pdf.set_fill_color(*MEGAPdf.BRAND_COLOR)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)

    for i, h in enumerate(headers):
        align = "R" if i >= 3 else "L"
        pdf.cell(col_widths[i], 8, h, fill=True, align=align)
    pdf.ln()

    # Items rows
    pdf.set_text_color(*MEGAPdf.DARK_TEXT)
    pdf.set_font("Helvetica", "", 9)
    row_fill = False

    for idx, item in enumerate(items, 1):
        if row_fill:
            pdf.set_fill_color(245, 247, 250)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.cell(col_widths[0], 7, str(idx), fill=True)
        pdf.cell(col_widths[1], 7, str(item.get("item_name", ""))[:35], fill=True)
        pdf.cell(col_widths[2], 7, str(item.get("description", ""))[:15], fill=True)
        pdf.cell(col_widths[3], 7, str(item.get("quantity", 1)), fill=True, align="R")
        pdf.cell(col_widths[4], 7, f"Rs.{item.get('unit_price', 0):,.2f}", fill=True, align="R")
        pdf.cell(col_widths[5], 7, f"Rs.{item.get('total_price', 0):,.2f}", fill=True, align="R")
        pdf.ln()

        if item.get("maintenance_schedule"):
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(col_widths[0], 5, "")
            pdf.cell(0, 5, f"Maintenance: {item['maintenance_schedule']}")
            pdf.ln()
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*MEGAPdf.DARK_TEXT)

        row_fill = not row_fill

    # Totals section
    pdf.ln(4)
    pdf.set_draw_color(*MEGAPdf.BRAND_COLOR)
    pdf.line(120, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(2)

    totals_x = 120
    val_x = 165

    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(totals_x, pdf.get_y())
    pdf.cell(val_x - totals_x, 6, "Subtotal:")
    pdf.cell(30, 6, f"Rs.{transaction.get('subtotal', 0):,.2f}", align="R", ln=True)

    if transaction.get("discount_percent", 0) > 0:
        pdf.set_xy(totals_x, pdf.get_y())
        pdf.cell(val_x - totals_x, 6, f"Discount ({transaction['discount_percent']}%):")
        pdf.cell(30, 6, f"-Rs.{transaction.get('discount_amount', 0):,.2f}", align="R", ln=True)

    if transaction.get("tax_rate", 0) > 0:
        pdf.set_xy(totals_x, pdf.get_y())
        pdf.cell(val_x - totals_x, 6, f"GST ({transaction['tax_rate']}%):")
        pdf.cell(30, 6, f"Rs.{transaction.get('tax_amount', 0):,.2f}", align="R", ln=True)

    pdf.ln(1)
    pdf.set_xy(totals_x, pdf.get_y())
    pdf.set_fill_color(*MEGAPdf.BRAND_COLOR)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(val_x - totals_x, 9, "TOTAL:", fill=True)
    pdf.cell(30, 9, f"Rs.{transaction.get('total_amount', 0):,.2f}", fill=True, align="R", ln=True)
    pdf.set_text_color(*MEGAPdf.DARK_TEXT)

    # Notes
    if transaction.get("notes"):
        pdf.ln(8)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Notes:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, transaction["notes"])

    # Terms
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, "Terms & Conditions:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    terms = [
        "1. This quotation is valid for 30 days from the date of issue.",
        "2. Payment terms: 50% deposit upon confirmation, balance upon completion.",
        "3. Warranty: 1 year on hardware, 90 days on installation workmanship.",
        "4. Prices are subject to change without prior notice.",
    ]
    for t in terms:
        pdf.cell(0, 5, t, ln=True)

    if not save_path:
        safe_name = (transaction.get("client_name") or "walkin").replace(" ", "_")
        filename = f"{doc_type}_{transaction['id']:04d}_{safe_name}.pdf"
        save_path = os.path.join(OUTPUT_DIR, filename)

    pdf.output(save_path)
    return save_path
