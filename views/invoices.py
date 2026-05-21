import os
import subprocess
import sys

from nicegui import ui

from models import (
    get_all_transactions,
    get_transaction,
    get_transaction_items,
    create_transaction,
    update_transaction_status,
    delete_transaction,
    decrement_stock,
)
from pdf_generator import generate_transaction_pdf
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
    SUCCESS,
    INPUT,
)
from views.transaction_builder import build_transaction_form


def render_invoices():
    user = CurrentUser.get()
    state = {"search": ""}
    list_panel = detail_panel = None

    def show_empty_detail():
        detail_panel.clear()
        with detail_panel:
            empty_state("Select an invoice or create a new one")

    def refresh_list():
        list_panel.clear()
        invoices = get_all_transactions(state["search"], tx_type="Invoice")
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
                        if can_export:
                            ghost_button("Export PDF", on_click=lambda e=iid: export_pdf(e))
                        if inv["status"] == "Pending":
                            success_button("Mark as Paid", on_click=lambda e=iid: mark_paid(e))
                        if can_delete:
                            danger_button("Delete", on_click=lambda e=iid: del_invoice(e))

    def save_invoice(**kwargs):
        tx_id = create_transaction(
            client_id=kwargs["client_id"],
            total_amount=kwargs["total"],
            subtotal=kwargs["subtotal"],
            tax_rate=kwargs["tax_rate"],
            tax_amount=kwargs["tax_amount"],
            discount_percent=kwargs["discount_percent"],
            discount_amount=kwargs["discount_amount"],
            tx_type="Invoice",
            status="Pending",
            notes=kwargs["notes"],
            items=kwargs["line_items"],
        )
        for item in kwargs["line_items"]:
            if item["item_type"] == "product":
                decrement_stock(item["item_id"], item["quantity"])
        notify_success(f"Invoice INV-{tx_id:04d} created!")
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

    def view_invoice(inv_id):
        tx = get_transaction(inv_id)
        items = get_transaction_items(inv_id)
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
                    if tx.get("discount_percent", 0) > 0:
                        lines.append(
                            (f"Discount ({tx['discount_percent']}%)", f"-₹{tx['discount_amount']:,.2f}")
                        )
                    if tx.get("tax_rate", 0) > 0:
                        lines.append((f"GST ({tx['tax_rate']}%)", f"₹{tx['tax_amount']:,.2f}"))
                    lines.append(("Total", f"₹{tx['total_amount']:,.2f}"))
                    for lbl, val in lines:
                        with ui.row().classes("w-full justify-between"):
                            ui.label(lbl).classes("font-bold" if lbl == "Total" else "")
                            ui.label(val).classes("font-bold" if lbl == "Total" else "")
                with ui.row().classes("gap-2"):
                    if user.has_permission("Export_PDF"):
                        ghost_button("Export PDF", on_click=lambda: export_pdf(inv_id))
                    if tx["status"] == "Pending":
                        success_button("Mark as Paid", on_click=lambda: mark_paid(inv_id))
                    ghost_button("Back", on_click=show_empty_detail)

    def export_pdf(inv_id):
        tx = get_transaction(inv_id)
        items = get_transaction_items(inv_id)
        if tx and items:
            path = generate_transaction_pdf(tx, items)
            notify_success(f"PDF saved to: {path}")
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif sys.platform == "win32":
                os.startfile(path)

    def mark_paid(inv_id):
        update_transaction_status(inv_id, "Paid")
        notify_success("Marked as Paid.")
        refresh_list()
        show_empty_detail()

    def del_invoice(inv_id):
        def do_delete():
            delete_transaction(inv_id)
            notify_success("Deleted.")
            refresh_list()
            show_empty_detail()

        confirm_dialog("Delete", "Delete this invoice?", do_delete)

    content = page_shell("Invoices", wide=True)
    with content:
        search = ui.input(placeholder="Search invoices...").props("outlined dense").classes(
            f"{INPUT} shrink-0"
        )
        search.on_value_change(lambda e: (state.update(search=e.value or ""), refresh_list()))
        if user.has_permission("Invoices_Create"):
            toolbar(search, add_label="Direct Invoice", on_add=show_builder)
        else:
            toolbar(search)
        list_panel, detail_panel = split_panels()
        refresh_list()
        show_empty_detail()
