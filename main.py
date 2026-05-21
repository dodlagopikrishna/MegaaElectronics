import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import app, ui
from nicegui.helpers.network import format_url

from database_setup import initialize_database, seed_sample_data
from login_manager import bootstrap_admin, CurrentUser
from ui_theme import (
    apply_page_background,
    APP_BODY,
    APP_FOOTER,
    BRAND_ACCENT,
    MAIN_PANE,
    MAIN_SCROLL,
    SIDEBAR,
    SIDEBAR_HEADER,
    TEXT_BRAND,
    TEXT_CAPTION,
    sidebar_nav_button,
    sidebar_user_menu,
    set_sidebar_nav_active,
)
from views.login import render_login_page
from views.dashboard import render_dashboard
from views.products import render_products
from views.clients import render_clients
from views.quotes import render_quotes
from views.invoices import render_invoices
from views.user_management import render_user_management
from views.change_password import render_change_password

initialize_database()
seed_sample_data()
bootstrap_admin()

NAV_PERMISSIONS = {
    "dashboard": "Dashboard",
    "products": "Products_View",
    "clients": "Clients_View",
    "quotes": "Quotes_View",
    "invoices": "Invoices_View",
    "users": "User_Management",
}

NAV_LABELS = {
    "dashboard": "Dashboard",
    "products": "Inventory",
    "clients": "Clients",
    "quotes": "Quotes",
    "invoices": "Invoices",
    "users": "User Mgmt",
}

NAV_ICONS = {
    "dashboard": "dashboard",
    "products": "inventory_2",
    "clients": "people",
    "quotes": "request_quote",
    "invoices": "receipt_long",
    "users": "manage_accounts",
}

VIEW_RENDERERS = {
    "dashboard": render_dashboard,
    "products": render_products,
    "clients": render_clients,
    "quotes": render_quotes,
    "invoices": render_invoices,
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
    order = ["dashboard", "products", "clients", "quotes", "invoices", "users"]
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
    state = {"view": allowed[0] if allowed else "dashboard"}
    nav_buttons = {}
    current = CurrentUser.get()

    def show_view(name: str):
        state["view"] = name
        for key, btn in nav_buttons.items():
            set_sidebar_nav_active(btn, active=(key == name))
        main_slot.clear()
        renderer = VIEW_RENDERERS.get(name, render_dashboard)
        with main_slot:
            with ui.column().classes("w-full flex-1 min-h-0 h-full flex flex-col"):
                renderer()

    def logout():
        CurrentUser.get().logout()
        ui.navigate.to("/login")

    with ui.row().classes(f"{APP_BODY} items-stretch"):
        with ui.column().classes(SIDEBAR):
            with ui.column().classes(SIDEBAR_HEADER):
                ui.label("MEGA").classes(f"{TEXT_BRAND} {BRAND_ACCENT}")
                ui.label("Electronics").classes(TEXT_CAPTION)

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

            role_subtitle = (
                ", ".join(current.role_names) if current.role_names else "MEGA Electronics"
            )
            with ui.column().classes("shrink-0 w-full mt-auto"):
                sidebar_user_menu(
                    display_name=current.display_name,
                    username=current.username,
                    subtitle=role_subtitle,
                    on_password=lambda: show_view("change_password"),
                    on_logout=logout,
                )

        with ui.column().classes(MAIN_PANE):
            main_slot = ui.column().classes(MAIN_SCROLL)
            show_view(state["view"])

    with ui.footer().classes(APP_FOOTER):
        ui.label("MEGA Electronics — Retail Management")
        ui.label("v2.0.0")


if __name__ in {"__main__", "__mp_main__"}:
    # Native desktop window via pywebview (no external browser tab).
    app.native.window_args["resizable"] = True
    app.native.window_args["min_size"] = (800, 500)
    app.native.window_args["url"] = format_url("http", NATIVE_HOST, NATIVE_PORT) + "/login"

    ui.run(
        title="MEGA Electronics - Retail Management",
        native=True,
        window_size=WINDOW_SIZE,
        reload=False,
        show=False,
        host=NATIVE_HOST,
        port=NATIVE_PORT,
        storage_secret="mega-electronics-local-secret",
    )
