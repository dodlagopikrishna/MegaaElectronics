from nicegui import ui

from country_phone_codes import (
    DEFAULT_PHONE_LABEL,
    PHONE_CODE_OPTIONS,
    dial_code_from_selection,
    dial_code_to_label,
    format_phone,
    parse_phone,
)
from login_manager import (
    get_all_users,
    get_all_roles,
    create_user,
    update_user,
    reset_user_password,
    delete_user,
    CurrentUser,
    is_default_admin,
)
from database_setup import get_connection
from ui_theme import (
    page_shell,
    card,
    labeled_input,
    split_panels,
    form_actions_row,
    success_button,
    ghost_button,
    danger_button,
    empty_state,
    confirm_dialog,
    notify_warning,
    notify_success,
    PRIMARY,
    INPUT,
    TEXT_LABEL,
)


def render_user_management():
    state = {"editing_id": None}
    list_panel = detail_panel = None
    role_colors = {
        "Admin": "#ef4444",
        "Sales": "#10b981",
        "Inventory": PRIMARY,
        "Technician": "#8b5cf6",
    }

    def refresh_table():
        list_panel.clear()
        users = get_all_users()
        with list_panel:
            if not users:
                empty_state("No users found.")
                return
            for u in users:
                with card():
                    with ui.row().classes("w-full justify-between flex-wrap gap-2"):
                        with ui.column():
                            display = (u["full_name"] or "").strip() or u["username"]
                            if u["is_default_admin"]:
                                display += " (default)"
                            ui.label(display).classes("font-semibold")
                            ui.label(f"@{u['username']}").classes("text-sm text-gray-500")
                            with ui.row().classes("gap-1 flex-wrap"):
                                for rname in u["role_names"]:
                                    ui.badge(rname).style(
                                        f"background:{role_colors.get(rname, '#6b7280')}"
                                    )
                            status = "Active" if u["is_active"] else "Disabled"
                            color = "text-green-600" if u["is_active"] else "text-red-500"
                            ui.label(status).classes(f"text-sm {color}")
                        with ui.row().classes("gap-2"):
                            ghost_button("Edit", on_click=lambda uid=u["id"]: edit_user(uid))
                            ghost_button("Reset Password", on_click=lambda uid=u["id"]: reset_pw(uid))
                            uid = u["id"]
                            if uid != CurrentUser.get().user_id and not u["is_default_admin"]:
                                danger_button("Delete", on_click=lambda i=uid: del_user(i))

    def show_empty_form():
        state["editing_id"] = None
        detail_panel.clear()
        with detail_panel:
            empty_state("Select a user to edit or click 'Add User'")

    def show_form(data=None):
        state["editing_id"] = data["id"] if data else None
        is_def = data and data.get("is_default_admin", False)
        detail_panel.clear()
        with detail_panel:
            with card():
                ui.label("Edit User" if data else "Add User").classes("text-lg font-bold mb-3")
                full_name = labeled_input(
                    "Full Name",
                    placeholder="Display name only (not used for login)",
                )
                username = labeled_input("Username")
                password = None
                if not data:
                    password = labeled_input("Password", password=True)

                ui.label("Phone (for WhatsApp)").classes(TEXT_LABEL)
                with ui.row().classes("w-full gap-2 items-start flex-nowrap"):
                    phone_code = (
                        ui.select(PHONE_CODE_OPTIONS, value=DEFAULT_PHONE_LABEL, with_input=True)
                        .props("outlined dense")
                        .classes("shrink-0 w-44 sm:w-52")
                    )
                    phone_number = (
                        ui.input(placeholder="Phone number")
                        .props("outlined dense")
                        .classes(f"{INPUT} flex-grow min-w-0")
                    )

                active_switch = ui.switch(
                    "Active (can sign in)",
                    value=True if not data else bool(data["is_active"]),
                )

                role_vars = {}
                if is_def:
                    ui.label("Admin (cannot change roles for default admin)").classes(
                        "text-sm text-orange-500"
                    )
                else:
                    ui.label("Roles").classes("text-sm font-medium text-gray-700")
                    existing = set(data["role_ids"]) if data else set()
                    for role in get_all_roles():
                        cb = ui.checkbox(role["role_name"], value=role["id"] in existing)
                        role_vars[role["id"]] = cb

                if data:
                    full_name.value = data.get("full_name") or ""
                    username.value = data["username"]
                    code, number = parse_phone(data.get("phone", ""))
                    phone_code.value = dial_code_to_label(code)
                    phone_number.value = number

                def save():
                    fn = (full_name.value or "").strip()
                    un = (username.value or "").strip()
                    if not fn:
                        notify_warning("Full name is required.")
                        return
                    if not un:
                        notify_warning("Username is required.")
                        return
                    ph = format_phone(
                        dial_code_from_selection(phone_code.value),
                        phone_number.value,
                    )
                    is_active = int(active_switch.value)
                    if (
                        state["editing_id"]
                        and state["editing_id"] == CurrentUser.get().user_id
                        and not is_active
                    ):
                        notify_warning("You cannot disable your own account while signed in.")
                        return
                    editing_def = state["editing_id"] and is_default_admin(state["editing_id"])
                    if editing_def:
                        selected = None
                    else:
                        selected = [rid for rid, cb in role_vars.items() if cb.value]
                        if not selected:
                            notify_warning("Select at least one role.")
                            return

                    if state["editing_id"]:
                        try:
                            if editing_def:
                                conn = get_connection()
                                conn.execute(
                                    """UPDATE users SET full_name = ?, username = ?, phone = ?, is_active = ?
                                       WHERE id = ?""",
                                    (fn, un, ph, is_active, state["editing_id"]),
                                )
                                conn.commit()
                                conn.close()
                            else:
                                update_user(state["editing_id"], fn, un, selected, is_active, phone=ph)
                        except Exception as e:
                            notify_warning(f"Could not update user: {e}")
                            return
                    else:
                        pw = (password.value or "").strip()
                        if len(pw) < 4:
                            notify_warning("Password must be at least 4 characters.")
                            return
                        try:
                            create_user(fn, un, pw, selected, is_active=is_active, phone=ph)
                        except Exception as e:
                            notify_warning(f"Could not create user: {e}")
                            return
                    notify_success("User saved.")
                    refresh_table()
                    show_empty_form()

                with form_actions_row():
                    success_button("Save", on_click=save)
                    ghost_button("Cancel", on_click=show_empty_form)

    def edit_user(user_id):
        for u in get_all_users():
            if u["id"] == user_id:
                show_form(u)
                break

    def reset_pw(user_id):
        with ui.dialog() as dialog, card():
            ui.label("Reset Password").classes("text-lg font-bold")
            pw = labeled_input("New Password", password=True)

            def apply():
                new_pw = (pw.value or "").strip()
                if new_pw and len(new_pw) >= 4:
                    reset_user_password(user_id, new_pw)
                    notify_success("Password has been reset.")
                    dialog.close()
                elif new_pw:
                    notify_warning("Password must be at least 4 characters.")

            with ui.row().classes("gap-2 mt-4 justify-end w-full"):
                ghost_button("Cancel", on_click=dialog.close)
                success_button("Reset Password", on_click=apply)
        dialog.open()

    def del_user(user_id):
        if is_default_admin(user_id):
            notify_warning("The default admin account cannot be deleted.")
            return

        def do_del():
            delete_user(user_id)
            notify_success("User deleted.")
            refresh_table()
            show_empty_form()

        confirm_dialog("Delete User", "Delete this user permanently?", do_del)

    content = page_shell("User Management", wide=True)
    with content:
        with ui.row().classes("w-full justify-end shrink-0"):
            success_button("Add User", on_click=lambda: show_form())
        list_panel, detail_panel = split_panels()
        refresh_table()
        show_empty_form()
