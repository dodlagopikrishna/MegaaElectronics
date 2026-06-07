from nicegui import ui

from country_phone_codes import (
    DEFAULT_PHONE_LABEL,
    PHONE_CODE_OPTIONS,
    dial_code_from_selection,
    dial_code_to_label,
    format_phone,
    parse_phone,
)
from models import (
    get_all_clients,
    add_client,
    update_client,
    delete_client,
    get_client,
    get_client_referrer,
    get_client_with_referrals,
    set_client_referrer,
    clear_client_referrer,
)
from text_utils import to_title_case
from login_manager import CurrentUser, get_active_users_with_phone
from whatsapp_share import share_client_via_whatsapp
from ui_theme import (
    page_shell,
    card,
    labeled_input,
    labeled_textarea,
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
    INPUT,
    TEXT_LABEL,
    TEXT_HEADING,
    TEXT_BODY,
    CARD,
)

_NONE_REFERRER = "-- None --"


def _parse_client_option(value):
    if not value or value == _NONE_REFERRER:
        return None
    return int(value.split(":", 1)[0])


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
                            addr = (c.get("address") or "").strip() or "—"
                            loc = (c.get("location") or "").strip()
                            detail = f"{c['phone']} · {addr}"
                            if loc:
                                detail += " · Map link"
                            ui.label(detail).classes("text-sm text-gray-500")
                        with ui.row().classes("gap-2"):
                            ghost_button(
                                "View",
                                on_click=lambda cid=c["id"]: view_client(cid),
                            )
                            ghost_button(
                                "WhatsApp",
                                on_click=lambda client=c: _share_client(client),
                            )
                            if can_edit:
                                ghost_button("Edit", on_click=lambda cid=c["id"]: edit_client(cid))
                            if can_delete:
                                danger_button("Delete", on_click=lambda cid=c["id"]: del_client(cid))

    def _share_client(client):
        system_users = get_active_users_with_phone()
        if not system_users:
            notify_warning("No system users have a phone number configured. Add phone numbers in User Management.")
            return

        with ui.dialog() as dialog, ui.card().classes(f"{CARD} p-4 min-w-[320px]"):
            ui.label("Send Client Details via WhatsApp").classes(TEXT_HEADING)
            ui.label(f"Select a team member to receive details of {client['name']}:").classes(TEXT_BODY)
            with ui.column().classes("w-full gap-2 mt-3 max-h-64 overflow-y-auto"):
                for su in system_users:
                    label = f"{su['display_name']} ({su['roles']})"

                    def on_select(d=dialog, phone=su["phone"], c=client):
                        d.close()
                        share_client_via_whatsapp(c, phone)
                        notify_success("Opening WhatsApp…")

                    ghost_button(label, on_click=on_select)
            with ui.row().classes("w-full justify-end mt-3"):
                ghost_button("Cancel", on_click=dialog.close)
        dialog.open()

    def show_empty_form():
        state["editing_id"] = None
        detail_panel.clear()
        with detail_panel:
            empty_state("Select a client to view or edit, or click 'Add Client'")

    def _display_value(value):
        text = (value or "").strip()
        return text if text else "—"

    def view_client(client_id):
        data = get_client_with_referrals(client_id)
        if not data:
            return
        detail_panel.clear()
        with detail_panel:
            with ui.column().classes("w-full gap-3"):
                ui.label(data["name"]).classes("text-xl font-bold")
                with card():
                    fields = [
                        ("Name", _display_value(data.get("name"))),
                        ("Phone", _display_value(data.get("phone"))),
                        ("Email", _display_value(data.get("email"))),
                        ("Address", _display_value(data.get("address"))),
                    ]
                    for label, value in fields:
                        with ui.row().classes("w-full justify-between py-1 gap-4"):
                            ui.label(label).classes("text-sm font-medium text-gray-600 shrink-0")
                            ui.label(value).classes("text-sm font-semibold text-right break-words")
                    with ui.row().classes("w-full justify-between py-1 gap-4"):
                        ui.label("Location").classes("text-sm font-medium text-gray-600 shrink-0")
                        loc = (data.get("location") or "").strip()
                        if loc:
                            ui.link("Google Maps link", loc, new_tab=True).classes("text-sm font-semibold")
                        else:
                            ui.label("—").classes("text-sm font-semibold")
                    with ui.row().classes("w-full justify-between py-1 gap-4"):
                        ui.label("Referred By").classes("text-sm font-medium text-gray-600 shrink-0")
                        referrer = data.get("referrer")
                        if referrer:
                            ghost_button(
                                referrer["name"],
                                on_click=lambda rid=referrer["id"]: view_client(rid),
                            )
                        else:
                            ui.label("—").classes("text-sm font-semibold")
                    ui.separator()
                    ui.label("Referred Clients").classes("text-sm font-medium text-gray-600")
                    referred = data.get("referred_clients") or []
                    if not referred:
                        ui.label("—").classes("text-sm font-semibold")
                    else:
                        with ui.column().classes("w-full gap-1"):
                            for rc in referred:
                                with ui.row().classes("w-full justify-between items-center gap-2"):
                                    ui.label(rc["name"]).classes("text-sm font-semibold")
                                    ghost_button(
                                        "View",
                                        on_click=lambda cid=rc["id"]: view_client(cid),
                                    )
                with ui.row().classes("gap-2 flex-wrap"):
                    ghost_button("WhatsApp", on_click=lambda: _share_client(data))
                    ghost_button("Back", on_click=show_empty_form)

    def show_form(data=None):
        state["editing_id"] = data["id"] if data else None
        detail_panel.clear()
        with detail_panel:
            with card():
                ui.label("Edit Client" if data else "Add Client").classes("text-lg font-bold mb-3")
                name = labeled_input("Name", title_case=True)
                ui.label("Phone").classes(TEXT_LABEL)
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
                email = labeled_input("Email")
                address = labeled_textarea("Address", title_case=True)
                location = labeled_input("Location (Google Maps URL)")

                referrer_sel = None
                if user.has_permission("Clients_Edit"):
                    all_clients = get_all_clients()
                    exclude_id = state["editing_id"]
                    referrer_opts = [_NONE_REFERRER] + [
                        f"{c['id']}: {c['name']}"
                        for c in all_clients
                        if c["id"] != exclude_id
                    ]
                    referrer_sel = labeled_select("Referred By", referrer_opts)

                if data:
                    name.value = data["name"]
                    code, number = parse_phone(data.get("phone", ""))
                    phone_code.value = dial_code_to_label(code)
                    phone_number.value = number
                    email.value = data.get("email", "")
                    address.value = data.get("address", "")
                    location.value = data.get("location", "")
                    if referrer_sel:
                        referrer = get_client_referrer(data["id"])
                        if referrer:
                            referrer_sel.value = f"{referrer['id']}: {referrer['name']}"
                        else:
                            referrer_sel.value = _NONE_REFERRER

                def save():
                    n = to_title_case((name.value or "").strip())
                    if not n:
                        notify_warning("Client name is required.")
                        return
                    ph = format_phone(
                        dial_code_from_selection(phone_code.value),
                        phone_number.value,
                    )
                    em = (email.value or "").strip()
                    ad = to_title_case((address.value or "").strip())
                    loc = (location.value or "").strip()
                    if state["editing_id"]:
                        client_id = state["editing_id"]
                        update_client(client_id, n, ph, em, ad, loc)
                    else:
                        client_id = add_client(n, ph, em, ad, loc)

                    if referrer_sel:
                        referrer_id = _parse_client_option(referrer_sel.value)
                        try:
                            if referrer_id is None:
                                clear_client_referrer(client_id)
                            else:
                                set_client_referrer(client_id, referrer_id)
                        except ValueError as exc:
                            notify_warning(str(exc))
                            return

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
            try:
                delete_client(client_id)
            except ValueError as exc:
                notify_warning(str(exc))
                return
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
