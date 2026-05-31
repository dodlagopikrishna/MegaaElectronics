from nicegui import ui

from models import (
    get_all_products,
    add_product,
    update_product,
    delete_product,
    get_product,
    get_all_services,
    add_service,
    update_service,
    delete_service,
    get_service,
)
from login_manager import CurrentUser
from ui_theme import (
    page_shell,
    card,
    labeled_input,
    labeled_select,
    split_panels,
    form_actions_row,
    toolbar,
    success_button,
    ghost_button,
    danger_button,
    empty_state,
    confirm_dialog,
    notify_warning,
    notify_success,
    TAB_ACTIVE,
    TAB_INACTIVE,
    BTN_PROPS,
    INPUT,
)


def render_products():
    user = CurrentUser.get()
    state = {"tab": "products", "editing_id": None, "search": ""}
    list_panel = detail_panel = tab_row = None

    def refresh_table():
        list_panel.clear()
        search = state["search"]
        with list_panel:
            if state["tab"] == "products":
                items = get_all_products(search)
                show_cost = user.has_permission("Cost_Prices")
                can_edit = user.has_permission("Products_Edit")
                can_delete = user.has_permission("Products_Delete")
                if not items:
                    empty_state("No products found.")
                    return
                for item in items:
                    stock_cls = "text-red-500" if item["stock_count"] <= 5 else ""
                    lines = [
                        item["category"],
                        f"Sell: ₹{item['sell_price']:.2f}",
                        f"Stock: {item['stock_count']} {item['unit']}",
                    ]
                    if show_cost:
                        lines.insert(1, f"Buy: ₹{item['buy_price']:.2f}")
                    _item_card(item["name"], lines, stock_cls, item["id"], can_edit, can_delete, "product")
            else:
                items = get_all_services(search)
                show_cost = user.has_permission("Cost_Prices")
                can_edit = user.has_permission("Services_Edit")
                can_delete = user.has_permission("Services_Delete")
                if not items:
                    empty_state("No services found.")
                    return
                for item in items:
                    lines = [item["service_type"], f"Charge: ₹{item['rate']:.2f}", item["rate_type"]]
                    if show_cost:
                        lines.insert(1, f"Worker: ₹{item.get('worker_cost', 0):.2f}")
                    _item_card(item["name"], lines, "", item["id"], can_edit, can_delete, "service")

    def _item_card(name, lines, extra_cls, item_id, can_edit, can_delete, kind):
        with card():
            with ui.row().classes("w-full justify-between flex-wrap gap-2"):
                with ui.column():
                    ui.label(name).classes("font-semibold")
                    ui.label(" · ".join(lines)).classes(f"text-sm text-gray-500 {extra_cls}")
                if can_edit or can_delete:
                    with ui.row().classes("gap-2"):
                        if can_edit:
                            ghost_button("Edit", on_click=lambda i=item_id, k=kind: edit_item(i, k))
                        if can_delete:
                            danger_button("Delete", on_click=lambda i=item_id, k=kind: delete_item(i, k))

    def show_empty_form():
        state["editing_id"] = None
        detail_panel.clear()
        with detail_panel:
            empty_state("Select an item to edit or click 'Add New'")

    def show_product_form(data=None):
        state["editing_id"] = data["id"] if data else None
        show_cost = user.has_permission("Cost_Prices")
        detail_panel.clear()
        with detail_panel:
            with card():
                ui.label("Edit Product" if data else "Add Product").classes("text-lg font-bold mb-3")
                name = labeled_input("Name")
                category = labeled_select(
                    "Category", ["CCTV", "Projector", "Accessories", "Other"]
                )
                cost = labeled_input("Buy Price (₹)") if show_cost else None
                retail = labeled_input("Sell Price (₹)")
                stock = labeled_input("Stock Quantity")
                unit = labeled_select("Unit", ["pcs", "meters", "sets", "rolls"])
                if data:
                    name.value = data["name"]
                    category.value = data["category"]
                    if cost:
                        cost.value = str(data["buy_price"])
                    retail.value = str(data["sell_price"])
                    stock.value = str(data["stock_count"])
                    unit.value = data["unit"]

                def save():
                    try:
                        n = (name.value or "").strip()
                        if not n:
                            notify_warning("Product name is required.")
                            return
                        c = float(cost.value or 0) if cost else 0
                        r = float(retail.value or 0)
                        s = int(stock.value or 0)
                        if state["editing_id"]:
                            if not cost:
                                existing = get_product(state["editing_id"])
                                if existing:
                                    c = existing["buy_price"]
                            update_product(
                                state["editing_id"], n, category.value, c, r, s, unit.value
                            )
                        else:
                            add_product(n, category.value, c, r, s, unit.value)
                        notify_success("Product saved.")
                        refresh_table()
                        show_empty_form()
                    except ValueError:
                        notify_warning("Enter valid numeric values for prices and stock.")

                with form_actions_row():
                    success_button("Save", on_click=save)
                    ghost_button("Cancel", on_click=show_empty_form)

    def show_service_form(data=None):
        state["editing_id"] = data["id"] if data else None
        show_cost = user.has_permission("Cost_Prices")
        detail_panel.clear()
        with detail_panel:
            with card():
                ui.label("Edit Service" if data else "Add Service").classes("text-lg font-bold mb-3")
                name = labeled_input("Name")
                desc = labeled_input("Description")
                rate = labeled_input("Charge Rate (₹)")
                worker = labeled_input("Worker Cost (₹)") if show_cost else None
                rate_type = labeled_select("Rate Type", ["Flat Fee", "Hourly Rate"])
                svc_type = labeled_select("Service Type", ["Installation", "Maintenance"])
                if data:
                    name.value = data["name"]
                    desc.value = data.get("description", "")
                    rate.value = str(data["rate"])
                    if worker:
                        worker.value = str(data.get("worker_cost", 0))
                    rate_type.value = data["rate_type"]
                    svc_type.value = data["service_type"]

                def save():
                    try:
                        n = (name.value or "").strip()
                        if not n:
                            notify_warning("Service name is required.")
                            return
                        wc = float(worker.value or 0) if worker else 0
                        if state["editing_id"] and not worker:
                            existing = get_service(state["editing_id"])
                            if existing:
                                wc = existing.get("worker_cost", 0)
                        if state["editing_id"]:
                            update_service(
                                state["editing_id"],
                                n,
                                (desc.value or "").strip(),
                                float(rate.value or 0),
                                wc,
                                rate_type.value,
                                svc_type.value,
                            )
                        else:
                            add_service(
                                n,
                                (desc.value or "").strip(),
                                float(rate.value or 0),
                                wc,
                                rate_type.value,
                                svc_type.value,
                            )
                        notify_success("Service saved.")
                        refresh_table()
                        show_empty_form()
                    except ValueError:
                        notify_warning("Enter valid numeric rates.")

                with form_actions_row():
                    success_button("Save", on_click=save)
                    ghost_button("Cancel", on_click=show_empty_form)

    def edit_item(item_id, kind):
        if kind == "product":
            data = get_product(item_id)
            if data:
                show_product_form(data)
        else:
            data = get_service(item_id)
            if data:
                show_service_form(data)

    def delete_item(item_id, kind):
        msg = "Delete this product?" if kind == "product" else "Delete this service?"
        fn = delete_product if kind == "product" else delete_service

        def do_delete():
            fn(item_id)
            notify_success("Deleted.")
            refresh_table()
            show_empty_form()

        confirm_dialog("Confirm", msg, do_delete)

    def switch_tab(tab):
        state["tab"] = tab
        state["editing_id"] = None
        tab_row.clear()
        with tab_row:
            ui.button("Products", on_click=lambda: switch_tab("products")).props(
                BTN_PROPS
            ).classes(TAB_ACTIVE if tab == "products" else TAB_INACTIVE)
            ui.button("Services", on_click=lambda: switch_tab("services")).props(
                BTN_PROPS
            ).classes(TAB_ACTIVE if tab == "services" else TAB_INACTIVE)
        refresh_table()
        show_empty_form()

    content = page_shell("Product & Service Catalog", wide=True)
    with content:
        tab_row = ui.row().classes("gap-2 w-full shrink-0")

        search = ui.input(placeholder="Search...").props("outlined dense").classes(
            f"{INPUT} shrink-0"
        )
        search.on_value_change(lambda e: (state.update(search=e.value or ""), refresh_table()))
        can_edit = user.has_permission("Products_Edit") or user.has_permission("Services_Edit")
        if can_edit:
            toolbar(
                search,
                add_label="Add New",
                on_add=lambda: (
                    show_product_form() if state["tab"] == "products" else show_service_form()
                ),
            )
        else:
            toolbar(search)

        list_panel, detail_panel = split_panels(
            panel_height="height: calc(100dvh - 17rem); max-height: calc(100dvh - 17rem);"
        )
        switch_tab("products")
