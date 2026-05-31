import os
import subprocess
import sys
import time

from nicegui import ui

from models import (
    get_all_transactions,
    get_transaction,
    get_transaction_items,
    create_transaction,
    update_transaction,
    delete_transaction,
    convert_estimate_to_invoice,
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
    empty_state,
    confirm_dialog,
    notify_success,
    notify_error,
    show_pdf_in_detail_panel,
    SUCCESS,
    INPUT,
)
from views.transaction_builder import build_transaction_form


def render_quotes():
    user = CurrentUser.get()
    state = {"search": ""}
    list_panel = detail_panel = None

    def show_empty_detail():
        detail_panel.clear()
        with detail_panel:
            empty_state("Select an estimate or create a new one")

    def refresh_list():
        list_panel.clear()
        estimates = get_all_transactions(state["search"], tx_type="Estimate")
        can_edit = user.has_permission("Quotes_Create")
        can_delete = user.has_permission("Quotes_Delete")
        can_export = user.has_permission("Export_PDF")

        with list_panel:
            if not estimates:
                empty_state("No estimates yet.")
                return
            for est in estimates:
                eid = est["id"]
                with card(interactive=True):
                    ui.label(f"EST-{est['id']:04d}").classes("font-bold")
                    ui.label(f"{est.get('client_name', 'Walk-in')} · {est['date']}").classes(
                        "text-sm text-gray-500"
                    )
                    ui.label(f"₹{est['total_amount']:,.2f}").classes("font-semibold").style(
                        f"color:{SUCCESS}"
                    )
                    with ui.row().classes("gap-2 flex-wrap mt-2"):
                        ghost_button("View", on_click=lambda e=eid: view_estimate(e))
                        ghost_button("View PDF", on_click=lambda e=eid: view_pdf(e, on_back=show_empty_detail))
                        if can_edit:
                            ghost_button("Edit", on_click=lambda e=eid: show_edit_builder(e))
                        if can_export:
                            ghost_button("Export PDF", on_click=lambda e=eid: export_pdf(e))
                        ghost_button("Convert to Invoice", on_click=lambda e=eid: to_invoice(e))
                        if can_delete:
                            danger_button("Delete", on_click=lambda e=eid: del_estimate(e))

    def save_estimate(**kwargs):
        edit_id = kwargs.pop("tx_id", None)
        if edit_id:
            updated = update_transaction(
                tx_id=edit_id,
                client_id=kwargs["client_id"],
                total_amount=kwargs["total"],
                subtotal=kwargs["subtotal"],
                tax_rate=kwargs["tax_rate"],
                tax_amount=kwargs["tax_amount"],
                discount_percent=kwargs["discount_percent"],
                discount_amount=kwargs["discount_amount"],
                notes=kwargs["notes"],
                items=kwargs["line_items"],
            )
            if not updated:
                notify_error("Could not update estimate. It may have been converted or deleted.")
                return
            notify_success(f"Estimate EST-{edit_id:04d} updated!")
            refresh_list()
            view_estimate(edit_id)
            return

        tx_id = create_transaction(
            client_id=kwargs["client_id"],
            total_amount=kwargs["total"],
            subtotal=kwargs["subtotal"],
            tax_rate=kwargs["tax_rate"],
            tax_amount=kwargs["tax_amount"],
            discount_percent=kwargs["discount_percent"],
            discount_amount=kwargs["discount_amount"],
            tx_type="Estimate",
            status="Pending",
            notes=kwargs["notes"],
            items=kwargs["line_items"],
        )
        notify_success(f"Estimate EST-{tx_id:04d} saved!")
        refresh_list()
        show_empty_detail()

    def show_builder():
        build_transaction_form(
            detail_panel,
            title="New Estimate",
            save_label="Save Estimate",
            on_save=save_estimate,
            on_cancel=show_empty_detail,
        )

    def show_edit_builder(est_id):
        tx = get_transaction(est_id)
        items = get_transaction_items(est_id)
        if not tx or tx["type"] != "Estimate":
            return
        build_transaction_form(
            detail_panel,
            title=f"Edit Estimate EST-{est_id:04d}",
            save_label="Update Estimate",
            on_save=save_estimate,
            on_cancel=lambda: view_estimate(est_id),
            tx_id=est_id,
            initial_transaction=tx,
            initial_items=items,
        )

    def view_estimate(est_id):
        tx = get_transaction(est_id)
        items = get_transaction_items(est_id)
        if not tx:
            return
        detail_panel.clear()
        with detail_panel:
            with ui.column().classes("w-full gap-3"):
                ui.label(f"Estimate #{tx['id']:04d}").classes("text-xl font-bold")
                ui.label(f"Client: {tx.get('client_name', 'Walk-in')} · Date: {tx['date']}").classes(
                    "text-sm text-gray-500"
                )
                for item in items:
                    with card():
                        tag = "[P]" if item["item_type"] == "product" else "[S]"
                        with ui.row().classes("w-full justify-between"):
                            ui.label(f"{tag} {item['item_name']} ×{item['quantity']}")
                            ui.label(f"₹{item['total_price']:,.2f}").classes("font-semibold")
                        if item.get("maintenance_schedule"):
                            ui.label(f"Maint: {item['maintenance_schedule']}").classes(
                                "text-xs text-blue-500"
                            )
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
                if tx.get("notes"):
                    ui.label(f"Notes: {tx['notes']}").classes("text-sm text-gray-500")
                with ui.row().classes("gap-2"):
                    if user.has_permission("Quotes_Create"):
                        ghost_button("Edit", on_click=lambda: show_edit_builder(est_id))
                    ghost_button(
                        "View PDF",
                        on_click=lambda: view_pdf(est_id, on_back=lambda: view_estimate(est_id)),
                    )
                    if user.has_permission("Export_PDF"):
                        ghost_button("Export PDF", on_click=lambda: export_pdf(est_id))
                    ghost_button("Convert to Invoice", on_click=lambda: to_invoice(est_id))
                    ghost_button("Back", on_click=show_empty_detail)

    def view_pdf(est_id, *, on_back=None):
        tx = get_transaction(est_id)
        items = get_transaction_items(est_id)
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
            title=f"Estimate EST-{est_id:04d}",
            subtitle=f"{tx.get('client_name', 'Walk-in')} · {tx['date']}",
            on_back=on_back or show_empty_detail,
            on_whatsapp=send_whatsapp,
        )

    def export_pdf(est_id):
        tx = get_transaction(est_id)
        items = get_transaction_items(est_id)
        if tx and items:
            path = generate_transaction_pdf(tx, items)
            notify_success(f"PDF saved to: {path}")
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif sys.platform == "win32":
                os.startfile(path)

    def to_invoice(est_id):
        def do_convert():
            convert_estimate_to_invoice(est_id)
            notify_success("Estimate converted to Invoice.")
            refresh_list()
            show_empty_detail()

        confirm_dialog(
            "Convert",
            "Convert this estimate to an invoice? This will decrement stock for products.",
            do_convert,
        )

    def del_estimate(est_id):
        def do_delete():
            delete_transaction(est_id)
            notify_success("Deleted.")
            refresh_list()
            show_empty_detail()

        confirm_dialog("Delete", "Delete this estimate?", do_delete)

    content = page_shell("Quotations / Estimates", wide=True)
    with content:
        search = ui.input(placeholder="Search estimates...").props("outlined dense").classes(
            f"{INPUT} shrink-0"
        )
        search.on_value_change(lambda e: (state.update(search=e.value or ""), refresh_list()))
        if user.has_permission("Quotes_Create"):
            toolbar(search, add_label="New Estimate", on_add=show_builder)
        else:
            toolbar(search)
        list_panel, detail_panel = split_panels()
        refresh_list()
        show_empty_detail()
