from nicegui import ui

from login_manager import authenticate, CurrentUser
from ui_theme import (
    BRAND_ACCENT,
    CARD,
    TEXT_BRAND_HERO,
    TEXT_CAPTION,
    TEXT_HEADING,
    TEXT_MUTED,
    labeled_input,
    primary_button,
    apply_page_background,
)


def render_login_page():
    apply_page_background()

    with ui.column().classes("w-full min-h-screen items-center justify-center p-4"):
        with ui.column().classes("w-full max-w-md gap-2 items-center"):
            ui.label("MEGA").classes(f"{TEXT_BRAND_HERO} {BRAND_ACCENT}")
            ui.label("Electronics").classes("text-lg text-slate-500")
            ui.label("Retail Management System").classes(f"{TEXT_MUTED} mb-4")

            with ui.card().classes(f"{CARD} p-6 w-full"):
                ui.label("Sign In").classes(f"{TEXT_HEADING} mb-4 w-full")

                username = labeled_input("Username", placeholder="Enter username")
                password = labeled_input("Password", password=True, placeholder="Enter password")
                status = ui.label("").classes("text-red-500 text-sm w-full min-h-[1.25rem]")

                async def do_login():
                    u = (username.value or "").strip()
                    p = (password.value or "").strip()
                    if not u or not p:
                        status.text = "Please enter both fields"
                        return

                    user, permissions = authenticate(u, p)
                    if user is None:
                        status.text = "Invalid username or password"
                        return

                    CurrentUser.get().login(user, permissions)
                    ui.navigate.to("/")

                primary_button("Login", on_click=do_login)
                password.on("keydown.enter", do_login)
                username.on("keydown.enter", lambda: password.run_method("focus"))

                ui.timer(0.3, lambda: username.run_method("focus"), once=True)
