from nicegui import ui

from login_manager import CurrentUser, change_own_password
from ui_theme import (
    page_shell,
    card,
    labeled_input,
    split_panels,
    form_actions_row,
    success_button,
    ghost_button,
    notify_success,
    PRIMARY,
)


def render_change_password():
    user = CurrentUser.get()
    content = page_shell("Change Password", wide=True)

    with content:
        list_panel, detail_panel = split_panels(
            list_weight="lg:col-span-4", detail_weight="lg:col-span-8"
        )

        with list_panel:
            with card():
                ui.label("Your Account").classes("text-lg font-bold mb-3")
                ui.label("Full Name").classes("text-sm text-gray-500")
                ui.label(user.display_name).classes("font-semibold mb-2")
                ui.label("Username").classes("text-sm text-gray-500")
                ui.label(user.username).classes("font-semibold mb-2")
                ui.label("Roles").classes("text-sm text-gray-500")
                roles = ", ".join(user.role_names) if user.role_names else "None"
                ui.label(roles).classes("font-semibold").style(f"color:{PRIMARY}")

        with detail_panel:
            with card():
                ui.label("New Password").classes("text-lg font-bold mb-3")
                new_pw = labeled_input("New Password", password=True)
                confirm_pw = labeled_input("Confirm New Password", password=True)
                ui.label("Minimum 4 characters.").classes("text-xs text-gray-500")
                status = ui.label("").classes("text-red-500 text-sm")

                def clear_form():
                    new_pw.value = ""
                    confirm_pw.value = ""
                    status.text = ""

                def save():
                    p1 = (new_pw.value or "").strip()
                    p2 = (confirm_pw.value or "").strip()
                    if not p1:
                        status.text = "Enter a new password."
                        return
                    if p1 != p2:
                        status.text = "New passwords do not match."
                        return
                    ok, message = change_own_password(p1)
                    if ok:
                        notify_success("Your password has been changed.")
                        clear_form()
                    else:
                        status.text = message

                with form_actions_row():
                    success_button("Save Password", on_click=save)
                    ghost_button("Clear", on_click=clear_form)
