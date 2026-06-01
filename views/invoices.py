import os
import subprocess
import sys
import time

from nicegui import ui

from models import (
    get_invoices,
    count_invoices,
    get_invoice,
    get_invoice_items,
    create_invoice,
    update_invoice_status,
    delete_invoice,
    decrement_stock,
)
from pdf_generator import generate_transaction_pdf
from whatsapp_share import share_transaction_pdf_via_whatsapp
from login_manager import CurrentUser
from ui_theme import (
    page_shell,
    card,
    split_panels,
    toolbar,
    ghost_button,
    danger_button,
    success_button,
    empty_state,
    confirm_dialog,
    notify_success,
    show_pdf_in_detail_panel,
    SUCCESS,
    INPUT,
)
from views.transaction_builder import build_transaction_form

PAGE_SIZE = 50


def render_invoices():
    user = CurrentUser.get()
    state = {"search": "", "page": 0, "sort": "number_desc"}
    list_panel = detail_panel = None

    def show_empty_detail():
        detail_panel.clear()
        with detail_panel:
            empty_state("Select an invoice or create a new one")

    def refresh_list():
        list_panel.clear()
        total = count_invoices(state["search"])
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        if state["page"] >= total_pages:
            state["page"] = max(0, total_pages - 1)
        offset = state["page"] * PAGE_SIZE
        invoices = get_invoices(state["search"], limit=PAGE_SIZE, offset=offset)
        if state["sort"] == "status_pending":
            invoices = sorted(invoices, key=lambda x: (0 if x["status"] == "Pending" else 1, -x["id"]))
        else:
            invoices = sorted(invoices, key=lambda x: -x["id"])
        can_delete = user.has_permission("Invoices_Delete")
        can_export = user.has_permission("Export_PDF")

        with list_panel:
            if not invoices:
                empty_state("No invoices yet.")
                return
            for inv in invoices:
                iid = inv["id"]
                status_color = SUCCESS if inv["status"] == "Paid" else "#e67e22"
                with card(interactive=True):
                    ui.label(f"INV-{inv['id']:04d}").classes("font-bold")
                    ui.label(f"{inv.get('client_name', 'Walk-in')} · {inv['date']}").classes(
                        "text-sm text-gray-500"
                    )
                    ui.label(f"₹{inv['total_amount']:,.2f} [{inv['status']}]").classes(
                        "font-semibold"
                    ).style(f"color:{status_color}")
                    with ui.row().classes("gap-2 flex-wrap mt-2"):
                        ghost_button("View", on_click=lambda e=iid: view_invoice(e))
                        ghost_button("View PDF", on_click=lambda e=iid: view_pdf(e, on_back=show_empty_detail))
                        if can_export:
                            ghost_button("Export PDF", on_click=lambda e=iid: export_pdf(e))
                        if inv["status"] == "Pending":
                            success_button("Mark as Paid", on_click=lambda e=iid: mark_paid(e))
                        elif inv["status"] == "Paid":
                            ghost_button("Mark as UnPaid", on_click=lambda e=iid: mark_unpaid(e))
                        if can_delete:
                            danger_button("Delete", on_click=lambda e=iid: del_invoice(e))
            if total_pages > 1:
                with ui.row().classes("w-full justify-center items-center gap-3 mt-2"):
                    if state["page"] > 0:
                        ghost_button(
                            "Prev",
                            on_click=lambda: (state.update(page=state["page"] - 1), refresh_list()),
                        )
                    ui.label(f"Page {state['page'] + 1} of {total_pages} ({total} total)").classes(
                        "text-sm text-gray-500"
                    )
                    if state["page"] < total_pages - 1:
                        ghost_button(
                            "Next",
                            on_click=lambda: (state.update(page=state["page"] + 1), refresh_list()),
                        )

    def save_invoice(**kwargs):
        inv_id = create_invoice(
            client_id=kwargs["client_id"],
            total_amount=kwargs["total"],
            subtotal=kwargs["subtotal"],
            tax_enabled=kwargs["tax_enabled"],
            tax_rate=kwargs["tax_rate"],
            tax_amount=kwargs["tax_amount"],
            discount_type=kwargs.get("discount_type", "flat"),
            discount_percent=kwargs["discount_percent"],
            discount_amount=kwargs["discount_amount"],
            status="Pending",
            notes=kwargs["notes"],
            items=kwargs["line_items"],
        )
        for item in kwargs["line_items"]:
            if item["item_type"] == "product":
                decrement_stock(item["item_id"], item["quantity"])
        notify_success(f"Invoice INV-{inv_id:04d} created!")
        refresh_list()
        show_empty_detail()

    def show_builder():
        build_transaction_form(
            detail_panel,
            title="New Direct Invoice",
            save_label="Save Invoice",
            on_save=save_invoice,
            on_cancel=show_empty_detail,
        )

    def _tax_lines(tx):
        lines = []
        if tx.get("tax_enabled") or tx.get("tax_rate", 0) > 0:
            lines.append((f"GST ({tx['tax_rate']}%)", f"₹{tx['tax_amount']:,.2f}"))
        return lines

    def view_invoice(inv_id):
        tx = get_invoice(inv_id)
        items = get_invoice_items(inv_id)
        if not tx:
            return
        detail_panel.clear()
        status_color = SUCCESS if tx["status"] == "Paid" else "#e67e22"
        with detail_panel:
            with ui.column().classes("w-full gap-3"):
                ui.label(f"Invoice #{tx['id']:04d}").classes("text-xl font-bold")
                ui.label(
                    f"Client: {tx.get('client_name', 'Walk-in')} · "
                    f"Date: {tx['date']} · Status: {tx['status']}"
                ).classes("text-sm").style(f"color:{status_color}")
                for item in items:
                    with card():
                        tag = "[P]" if item["item_type"] == "product" else "[S]"
                        with ui.row().classes("w-full justify-between"):
                            ui.label(f"{tag} {item['item_name']} ×{item['quantity']}")
                            ui.label(f"₹{item['total_price']:,.2f}").classes("font-semibold")
                with card():
                    lines = [("Subtotal", f"₹{tx['subtotal']:,.2f}")]
                    if tx.get("discount_amount", 0) > 0 or tx.get("discount_percent", 0) > 0:
                        dtype = tx.get("discount_type", "flat")
                        if dtype == "flat":
                            disc_lbl = f"Discount (₹{tx['discount_percent']:,.2f} off)"
                        else:
                            disc_lbl = f"Discount ({tx['discount_percent']}%)"
                        lines.append((disc_lbl, f"-₹{tx['discount_amount']:,.2f}"))
                    lines.extend(_tax_lines(tx))
                    lines.append(("Total", f"₹{tx['total_amount']:,.2f}"))
                    for lbl, val in lines:
                        with ui.row().classes("w-full justify-between"):
                            ui.label(lbl).classes("font-bold" if lbl == "Total" else "")
                            ui.label(val).classes("font-bold" if lbl == "Total" else "")
                with ui.row().classes("gap-2"):
                    ghost_button("Back", on_click=show_empty_detail)

    def view_pdf(inv_id, *, on_back=None):
        tx = get_invoice(inv_id)
        items = get_invoice_items(inv_id)
        if not tx or not items:
            return
        path = generate_transaction_pdf(tx, items)
        filename = os.path.basename(path)
        pdf_url = f"/exports/{filename}?t={int(time.time())}"

        def send_whatsapp():
            share_transaction_pdf_via_whatsapp(tx, items)
            notify_success("Opening WhatsApp…")

        show_pdf_in_detail_panel(
            detail_panel,
            pdf_url=pdf_url,
            title=f"Invoice INV-{inv_id:04d}",
            subtitle=f"{tx.get('client_name', 'Walk-in')} · {tx['date']} · {tx['status']}",
            on_back=on_back or show_empty_detail,
            on_whatsapp=send_whatsapp,
        )

    def export_pdf(inv_id):
        tx = get_invoice(inv_id)
        items = get_invoice_items(inv_id)
        if tx and items:
            path = generate_transaction_pdf(tx, items)
            notify_success(f"PDF saved to: {path}")
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif sys.platform == "win32":
                os.startfile(path)

    def mark_paid(inv_id):
        def do_mark_paid():
            update_invoice_status(inv_id, "Paid")
            notify_success("Marked as Paid.")
            refresh_list()
            show_empty_detail()

        confirm_dialog("Mark as Paid", "Mark this invoice as paid?", do_mark_paid)

    def mark_unpaid(inv_id):
        def do_mark_unpaid():
            update_invoice_status(inv_id, "Pending")
            notify_success("Marked as UnPaid.")
            refresh_list()
            show_empty_detail()

        confirm_dialog("Mark as UnPaid", "Mark this invoice as unpaid?", do_mark_unpaid)

    def del_invoice(inv_id):
        def do_delete():
            delete_invoice(inv_id)
            notify_success("Deleted.")
            refresh_list()
            show_empty_detail()

        confirm_dialog("Delete", "Delete this invoice?", do_delete)

    content = page_shell("Invoices", wide=True)
    with content:
        search = ui.input(placeholder="Search invoices...").props("outlined dense").classes(
            f"{INPUT} shrink-0"
        )
        search.on_value_change(
            lambda e: (state.update(search=e.value or "", page=0), refresh_list())
        )
        if user.has_permission("Invoices_Create"):
            toolbar(search, add_label="Direct Invoice", on_add=show_builder)
        else:
            toolbar(search)

        sort_options = {
            "number_desc": "Invoice # (Newest First)",
            "status_pending": "Payment Status (Pending First)",
        }
        with ui.row().classes("w-full items-center gap-2 mb-2"):
            ui.label("Sort by:").classes("text-sm text-gray-600")
            ui.select(
                options=sort_options,
                value="number_desc",
                on_change=lambda e: (state.update(sort=e.value), refresh_list()),
            ).props("outlined dense").classes("min-w-[220px]")

        list_panel, detail_panel = split_panels()
        refresh_list()
        show_empty_detail()
