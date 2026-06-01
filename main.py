import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app_config
app_config.load_config()

from nicegui import app, ui
from nicegui.helpers.network import format_url

from database_setup import initialize_database
from login_manager import bootstrap_admin, CurrentUser
from pdf_generator import OUTPUT_DIR
from store_config import STORE_GSTIN, STORE_NAME, STORE_PHONE_DISPLAY, STORE_STORAGE_SECRET
from ui_theme import (
    ASSETS_DIR,
    apply_page_background,
    APP_BODY,
    APP_FOOTER,
    MAIN_PANE,
    MAIN_VIEW_HOST,
    MAIN_VIEW_SHELL,
    SIDEBAR,
    SIDEBAR_HEADER,
    VIEW_TRANSITION_MS,
    brand_logo,
    nav_view_direction,
    sidebar_nav_button,
    sidebar_user_menu,
    set_sidebar_nav_active,
    trigger_main_view_exit,
)

app.add_static_files("/assets", ASSETS_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.add_static_files("/exports", OUTPUT_DIR)
from views.login import render_login_page
from views.dashboard import render_dashboard
from views.products import render_products
from views.clients import render_clients
from views.quotes import render_quotes
from views.invoices import render_invoices
from views.maintenance import render_maintenance
from views.user_management import render_user_management
from views.change_password import render_change_password

initialize_database()
bootstrap_admin()

NAV_PERMISSIONS = {
    "dashboard": "Dashboard",
    "products": "Products_View",
    "clients": "Clients_View",
    "quotes": "Quotes_View",
    "invoices": "Invoices_View",
    "maintenance": "Maintenance_View",
    "users": "User_Management",
}

NAV_LABELS = {
    "dashboard": "Dashboard",
    "products": "Inventory",
    "clients": "Clients",
    "quotes": "Quotes",
    "invoices": "Invoices",
    "maintenance": "Maintenance Schedule",
    "users": "User Management",
}

NAV_ICONS = {
    "dashboard": "dashboard",
    "products": "inventory_2",
    "clients": "people",
    "quotes": "request_quote",
    "invoices": "receipt_long",
    "maintenance": "build_circle",
    "users": "manage_accounts",
}

VIEW_RENDERERS = {
    "dashboard": render_dashboard,
    "products": render_products,
    "clients": render_clients,
    "quotes": render_quotes,
    "invoices": render_invoices,
    "maintenance": render_maintenance,
    "users": render_user_management,
    "change_password": render_change_password,
}

WINDOW_SIZE = (1280, 780)
NATIVE_HOST = "127.0.0.1"
NATIVE_PORT = 8765


def _is_authenticated():
    return CurrentUser.get().is_authenticated


def _allowed_views():
    current = CurrentUser.get()
    order = ["dashboard", "products", "clients", "quotes", "invoices", "maintenance", "users"]
    return [k for k in order if current.has_permission(NAV_PERMISSIONS[k])]


@ui.page("/login")
def login_page():
    apply_page_background()
    if _is_authenticated():
        ui.navigate.to("/")
        return
    render_login_page()


@ui.page("/")
def home_page():
    if not _is_authenticated():
        ui.navigate.to("/login")
        return

    apply_page_background(lock_viewport=True)

    allowed = _allowed_views()
    nav_order = allowed + ["change_password"]
    state = {"view": allowed[0] if allowed else "dashboard", "mounted": False}
    nav_buttons = {}
    pending_view = {"name": None}
    swap_timer = {"handle": None}
    current = CurrentUser.get()

    def _mount_view(name: str, *, direction: str | None):
        state["view"] = name
        for key, btn in nav_buttons.items():
            set_sidebar_nav_active(btn, active=(key == name))
        main_slot.clear()
        renderer = VIEW_RENDERERS.get(name, render_dashboard)
        enter = f" view-enter-{direction}" if direction else ""
        with main_slot:
            with ui.column().classes(f"{MAIN_VIEW_SHELL}{enter}"):
                renderer()

    def show_view(name: str):
        if name == state["view"] and state["mounted"]:
            return
        pending_view["name"] = name

        if swap_timer["handle"] is not None:
            swap_timer["handle"].cancel()
            swap_timer["handle"] = None

        def complete_swap():
            swap_timer["handle"] = None
            target = pending_view["name"]
            if target is None:
                return
            direction = nav_view_direction(state["view"], target, nav_order)
            _mount_view(target, direction=direction)

        if not state["mounted"]:
            state["mounted"] = True
            _mount_view(name, direction=None)
            return

        direction = nav_view_direction(state["view"], name, nav_order)

        trigger_main_view_exit(direction)
        swap_timer["handle"] = ui.timer(
            VIEW_TRANSITION_MS / 1000.0,
            complete_swap,
            once=True,
        )

    def logout():
        CurrentUser.get().logout()
        ui.navigate.to("/login")

    with ui.row().classes(f"{APP_BODY} items-stretch"):
        with ui.column().classes(SIDEBAR):
            with ui.column().classes(SIDEBAR_HEADER):
                brand_logo(variant="sidebar")

            with ui.column().classes("shrink-0 px-3 py-4 gap-1 w-full"):
                for key in allowed:
                    label = NAV_LABELS[key]
                    icon = NAV_ICONS[key]

                    def make_nav(k=key):
                        def navigate():
                            show_view(k)

                        return navigate

                    btn = sidebar_nav_button(label, icon, on_click=make_nav())
                    nav_buttons[key] = btn

            role_subtitle = ", ".join(current.role_names) if current.role_names else "Staff"
            with ui.column().classes("shrink-0 w-full mt-auto"):
                sidebar_user_menu(
                    display_name=current.display_name,
                    username=current.username,
                    subtitle=role_subtitle,
                    on_password=lambda: show_view("change_password"),
                    on_logout=logout,
                )

        with ui.column().classes(MAIN_PANE):
            main_slot = ui.column().classes(MAIN_VIEW_HOST)
            show_view(state["view"])

    with ui.footer(fixed=False).classes(APP_FOOTER):
        ui.label(f"{STORE_NAME}  |  Tel: {STORE_PHONE_DISPLAY}  |  GSTIN: {STORE_GSTIN}")
        ui.label("Retail Management System v1.0.0")


if __name__ in {"__main__", "__mp_main__"}:
    # Native desktop window via pywebview (no external browser tab).
    app.native.window_args["resizable"] = True
    app.native.window_args["min_size"] = (800, 500)
    app.native.window_args["url"] = format_url("http", NATIVE_HOST, NATIVE_PORT) + "/login"

    ui.run(
        title=f"{STORE_NAME} - Retail Management System",
        native=True,
        window_size=WINDOW_SIZE,
        reload=False,
        show=False,
        host=NATIVE_HOST,
        port=NATIVE_PORT,
        storage_secret=STORE_STORAGE_SECRET,
    )
