"""Shared estimate/invoice builder UI for NiceGUI."""

from nicegui import ui

from models import get_all_clients, get_all_products, get_all_services
from ui_theme import (
    LIST_ROW,
    card,
    labeled_input,
    labeled_select,
    labeled_textarea,
    form_actions_row,
    success_button,
    ghost_button,
    danger_button,
    notify_warning,
    INPUT,
)


def calc_totals(line_items, tax_rate: float, discount_pct: float):
    subtotal = sum(item["total_price"] for item in line_items)
    discount_amt = subtotal * (discount_pct / 100)
    after_discount = subtotal - discount_amt
    tax_amt = after_discount * (tax_rate / 100)
    total = after_discount + tax_amt
    return subtotal, discount_amt, tax_amt, total


def build_transaction_form(
    detail_panel,
    *,
    title: str,
    save_label: str,
    on_save,
    on_cancel,
    tx_id=None,
    initial_transaction=None,
    initial_items=None,
):
    line_items = []
    if initial_items:
        for item in initial_items:
            line_items.append(
                {
                    "item_type": item["item_type"],
                    "item_id": item["item_id"],
                    "item_name": item["item_name"],
                    "description": item.get("description", ""),
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "total_price": item["total_price"],
                    "maintenance_schedule": item.get("maintenance_schedule", ""),
                }
            )

    detail_panel.clear()
    with detail_panel:
        with ui.column().classes("w-full gap-4"):
            ui.label(title).classes("text-xl font-bold")

            clients = get_all_clients()
            client_opts = ["-- Walk-in --"] + [f"{c['id']}: {c['name']}" for c in clients]
            client_sel = labeled_select("Client", client_opts)
            if initial_transaction and initial_transaction.get("client_id"):
                cid = initial_transaction["client_id"]
                cname = initial_transaction.get("client_name", "")
                client_sel.value = f"{cid}: {cname}"

            with card():
                ui.label("Add Item").classes("font-semibold mb-2")
                search = ui.input(
                    placeholder="Type to search products & services..."
                ).props("outlined dense").classes(INPUT)
                results_box = ui.column().classes("w-full gap-1")

            items_box = ui.column().classes("w-full gap-2")
            totals_label = ui.label("").classes("text-sm text-right text-gray-700 w-full")

            with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2"):
                tax_inp = labeled_input("Tax Rate (%)")
                tax_inp.value = (
                    str(initial_transaction["tax_rate"])
                    if initial_transaction
                    else "9"
                )
                discount_inp = labeled_input("Discount (%)")
                discount_inp.value = (
                    str(initial_transaction.get("discount_percent", 0))
                    if initial_transaction
                    else "0"
                )
                notes = labeled_textarea("Notes")
                if initial_transaction:
                    notes.value = initial_transaction.get("notes", "") or ""

            def get_rates():
                try:
                    tax_rate = float(tax_inp.value or 0)
                except ValueError:
                    tax_rate = 0
                try:
                    discount_pct = float(discount_inp.value or 0)
                except ValueError:
                    discount_pct = 0
                return tax_rate, discount_pct

            def update_totals():
                tax_rate, discount_pct = get_rates()
                sub, disc, tax, tot = calc_totals(line_items, tax_rate, discount_pct)
                totals_label.text = (
                    f"Subtotal: ₹{sub:,.2f}  |  Discount: -₹{disc:,.2f}  |  "
                    f"Tax: ₹{tax:,.2f}  |  Total: ₹{tot:,.2f}"
                )

            def refresh_lines():
                items_box.clear()
                with items_box:
                    if not line_items:
                        ui.label("No items added yet.").classes("text-gray-500 text-sm")
                        return
                    for idx, item in enumerate(line_items):
                        tag = "[P]" if item["item_type"] == "product" else "[S]"
                        with ui.row().classes(LIST_ROW):
                            ui.label(f"{tag} {item['item_name']}").classes("flex-grow text-sm")
                            qty = ui.number(value=item["quantity"], min=1, step=1).props(
                                "outlined dense"
                            ).classes("w-20")

                            def on_qty(e, i=idx, q=qty):
                                try:
                                    n = max(1, int(e.value))
                                except (TypeError, ValueError):
                                    n = 1
                                line_items[i]["quantity"] = n
                                line_items[i]["total_price"] = n * line_items[i]["unit_price"]
                                refresh_lines()
                                update_totals()

                            qty.on_value_change(on_qty)
                            ui.label(f"₹{item['total_price']:.2f}").classes(
                                "font-semibold text-sm"
                            )
                            danger_button(
                                "Remove",
                                on_click=lambda i=idx: (
                                    line_items.pop(i),
                                    refresh_lines(),
                                    update_totals(),
                                ),
                            )
                        if item["item_type"] == "service":
                            maint = ui.input(
                                placeholder="Maintenance schedule (e.g. Monthly)",
                                value=item.get("maintenance_schedule", ""),
                            ).props("outlined dense").classes(INPUT)

                            def on_maint(e, i=idx):
                                line_items[i]["maintenance_schedule"] = e.value or ""

                            maint.on_value_change(on_maint)
                update_totals()

            def do_search():
                results_box.clear()
                q = (search.value or "").strip()
                if not q:
                    return
                products = get_all_products(q)
                services = get_all_services(q)
                with results_box:
                    if not products and not services:
                        ui.label("No items found.").classes("text-gray-500 text-sm")
                        return
                    for p in products[:5]:

                        def add_p(item=p):
                            line_items.append(
                                {
                                    "item_type": "product",
                                    "item_id": item["id"],
                                    "item_name": item["name"],
                                    "description": item["category"],
                                    "quantity": 1,
                                    "unit_price": item["retail_price"],
                                    "total_price": item["retail_price"],
                                    "maintenance_schedule": "",
                                }
                            )
                            refresh_lines()

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label(
                                f"[P] {p['name']} — ₹{p['retail_price']:.2f} "
                                f"({p['stock_count']} in stock)"
                            ).classes("text-xs")
                            ghost_button("Add Product", on_click=add_p)
                    for s in services[:5]:

                        def add_s(item=s):
                            line_items.append(
                                {
                                    "item_type": "service",
                                    "item_id": item["id"],
                                    "item_name": item["name"],
                                    "description": item.get("description", ""),
                                    "quantity": 1,
                                    "unit_price": item["rate"],
                                    "total_price": item["rate"],
                                    "maintenance_schedule": "",
                                }
                            )
                            refresh_lines()

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label(
                                f"[S] {s['name']} — ₹{s['rate']:.2f} ({s['rate_type']})"
                            ).classes("text-xs")
                            ghost_button("Add Service", on_click=add_s)

            search.on("update:model-value", lambda _: ui.timer(0.25, do_search, once=True))
            refresh_lines()

            def save():
                if not line_items:
                    notify_warning("Add at least one item.")
                    return
                client_id = None
                sel = client_sel.value
                if sel and sel != "-- Walk-in --":
                    try:
                        client_id = int(str(sel).split(":")[0])
                    except ValueError:
                        pass
                tax_rate, discount_pct = get_rates()
                sub, disc, tax, tot = calc_totals(line_items, tax_rate, discount_pct)
                payload = dict(
                    client_id=client_id,
                    line_items=line_items,
                    subtotal=sub,
                    tax_rate=tax_rate,
                    tax_amount=tax,
                    discount_percent=discount_pct,
                    discount_amount=disc,
                    total=tot,
                    notes=(notes.value or "").strip(),
                )
                if tx_id is not None:
                    payload["tx_id"] = tx_id
                on_save(**payload)

            with form_actions_row():
                success_button(save_label, on_click=save)
                ghost_button("Cancel", on_click=on_cancel)
