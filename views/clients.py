from nicegui import ui

from models import get_all_clients, add_client, update_client, delete_client, get_client
from login_manager import CurrentUser
from ui_theme import (
    page_shell,
    card,
    labeled_input,
    labeled_textarea,
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
    INPUT,
)


def render_clients():
    user = CurrentUser.get()
    state = {"editing_id": None, "search": ""}
    list_panel = detail_panel = None

    def refresh_table():
        list_panel.clear()
        clients = get_all_clients(state["search"])
        can_edit = user.has_permission("Clients_Edit")
        can_delete = user.has_permission("Clients_Delete")

        with list_panel:
            if not clients:
                empty_state("No clients found.")
                return
            for c in clients:
                with card(interactive=True):
                    with ui.row().classes("w-full justify-between items-center flex-wrap gap-2"):
                        with ui.column().classes("gap-0"):
                            ui.label(c["name"]).classes("font-semibold")
                            ui.label(f"{c['phone']} · {c['email']}").classes("text-sm text-gray-500")
                        if can_edit or can_delete:
                            with ui.row().classes("gap-2"):
                                if can_edit:
                                    ghost_button("Edit", on_click=lambda cid=c["id"]: edit_client(cid))
                                if can_delete:
                                    danger_button("Delete", on_click=lambda cid=c["id"]: del_client(cid))

    def show_empty_form():
        state["editing_id"] = None
        detail_panel.clear()
        with detail_panel:
            empty_state("Select a client to edit or click 'Add Client'")

    def show_form(data=None):
        state["editing_id"] = data["id"] if data else None
        detail_panel.clear()
        with detail_panel:
            with card():
                ui.label("Edit Client" if data else "Add Client").classes("text-lg font-bold mb-3")
                name = labeled_input("Name")
                phone = labeled_input("Phone")
                email = labeled_input("Email")
                address = labeled_textarea("Address")
                if data:
                    name.value = data["name"]
                    phone.value = data.get("phone", "")
                    email.value = data.get("email", "")
                    address.value = data.get("address", "")

                def save():
                    n = (name.value or "").strip()
                    if not n:
                        notify_warning("Client name is required.")
                        return
                    ph = (phone.value or "").strip()
                    em = (email.value or "").strip()
                    ad = (address.value or "").strip()
                    if state["editing_id"]:
                        update_client(state["editing_id"], n, ph, em, ad)
                    else:
                        add_client(n, ph, em, ad)
                    notify_success("Client saved.")
                    refresh_table()
                    show_empty_form()

                with form_actions_row():
                    success_button("Save", on_click=save)
                    ghost_button("Cancel", on_click=show_empty_form)

    def edit_client(client_id):
        data = get_client(client_id)
        if data:
            show_form(data)

    def del_client(client_id):
        def do_delete():
            delete_client(client_id)
            notify_success("Client deleted.")
            refresh_table()
            show_empty_form()

        confirm_dialog("Delete Client", "Delete this client permanently?", do_delete)

    content = page_shell("Client Management", wide=True)
    with content:
        search = ui.input(placeholder="Search clients...").props("outlined dense").classes(
            f"{INPUT} shrink-0"
        )
        search.on_value_change(lambda e: (state.update(search=e.value or ""), refresh_table()))
        if user.has_permission("Clients_Edit"):
            toolbar(search, add_label="Add Client", on_add=lambda: show_form())
        else:
            toolbar(search)

        list_panel, detail_panel = split_panels()
        refresh_table()
        show_empty_form()
