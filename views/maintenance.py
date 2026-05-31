"""Maintenance Schedule management view for NiceGUI."""

import calendar
from datetime import date

from nicegui import ui

from models import (
    get_all_maintenance_schedules,
    get_maintenance_schedule,
    create_maintenance_schedule,
    update_maintenance_schedule,
    delete_maintenance_schedule,
    mark_maintenance_completed,
    get_all_clients,
    get_all_services,
)
from login_manager import CurrentUser
from ui_theme import (
    page_shell,
    card,
    labeled_input,
    labeled_select,
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
    TEXT_LABEL,
)

FREQUENCY_OPTIONS = ["Once", "Monthly", "Quarterly", "Half-Yearly", "Yearly"]
STATUS_OPTIONS = ["Active", "Completed", "Cancelled"]
_STATUS_COLORS = {"Active": "green", "Completed": "grey", "Cancelled": "red"}

_FREQ_MONTHS = {"Monthly": 1, "Quarterly": 3, "Half-Yearly": 6, "Yearly": 12}


def _compute_next_due(start_str: str, freq: str) -> str:
    """Return next due as YYYY-MM-DD: Once uses start date; recurring uses start + one interval."""
    if not start_str:
        return ""
    if freq == "Once":
        return start_str
    try:
        d = date.fromisoformat(start_str)
    except ValueError:
        return ""
    months = _FREQ_MONTHS.get(freq, 0)
    if months == 0:
        return ""
    total_months = d.month - 1 + months
    new_year = d.year + total_months // 12
    new_month = total_months % 12 + 1
    max_day = calendar.monthrange(new_year, new_month)[1]
    new_day = min(d.day, max_day)
    return date(new_year, new_month, new_day).isoformat()


def format_schedule_due(schedule: dict) -> str:
    due = (schedule.get("next_due_date") or "").strip()
    if due:
        return due
    start = (schedule.get("start_date") or "").strip()
    if schedule.get("frequency") == "Once" and start:
        return start
    return "N/A"


def render_maintenance():
    user = CurrentUser.get()
    state = {"editing_id": None, "search": ""}
    list_panel = detail_panel = None

    def refresh_list():
        list_panel.clear()
        schedules = get_all_maintenance_schedules(state["search"])
        can_edit = user.has_permission("Maintenance_Edit")
        can_delete = user.has_permission("Maintenance_Delete")

        with list_panel:
            if not schedules:
                empty_state("No maintenance schedules found.")
                return
            for s in schedules:
                sid = s["id"]
                badge_color = _STATUS_COLORS.get(s["status"], "grey")
                with card(interactive=True):
                    with ui.row().classes("w-full justify-between items-start flex-wrap gap-2"):
                        with ui.column().classes("gap-0 min-w-0"):
                            ui.label(s["client_name"]).classes("font-semibold")
                            ui.label(s["service_name"]).classes("text-sm text-gray-600")
                            ui.label(
                                f"{s['frequency']} · Due: {format_schedule_due(s)}"
                            ).classes("text-xs text-gray-500")
                        ui.badge(s["status"]).props(f"color={badge_color}")
                    with ui.row().classes("gap-2 mt-2 flex-wrap"):
                        ghost_button("View", on_click=lambda e=sid: view_schedule(e))
                        if can_edit:
                            ghost_button("Edit", on_click=lambda e=sid: show_form(get_maintenance_schedule(e)))
                        if can_delete:
                            danger_button("Delete", on_click=lambda e=sid: del_schedule(e))
                        if s["status"] != "Completed" and can_edit:
                            success_button(
                                "Mark as Completed",
                                on_click=lambda e=sid: do_mark_completed(e),
                            )

    def show_empty_detail():
        state["editing_id"] = None
        detail_panel.clear()
        with detail_panel:
            empty_state("Select a schedule or create a new one")

    def view_schedule(schedule_id):
        s = get_maintenance_schedule(schedule_id)
        if not s:
            return
        detail_panel.clear()
        can_edit = user.has_permission("Maintenance_Edit")
        can_delete = user.has_permission("Maintenance_Delete")
        badge_color = _STATUS_COLORS.get(s["status"], "grey")
        with detail_panel:
            with ui.column().classes("w-full gap-3"):
                with ui.row().classes("w-full justify-between items-start"):
                    ui.label(s["service_name"]).classes("text-xl font-bold")
                    ui.badge(s["status"]).props(f"color={badge_color}")
                with card():
                    fields = [
                        ("Client", s["client_name"]),
                        ("Service", s["service_name"]),
                        ("Frequency", s["frequency"]),
                        ("Start Date", s["start_date"]),
                        ("Next Due Date", format_schedule_due(s)),
                        ("Status", s["status"]),
                    ]
                    for label, value in fields:
                        with ui.row().classes("w-full justify-between py-1"):
                            ui.label(label).classes("text-sm font-medium text-gray-600")
                            ui.label(str(value)).classes("text-sm font-semibold")
                    if s.get("notes"):
                        ui.separator()
                        ui.label("Notes").classes("text-sm font-medium text-gray-600")
                        ui.label(s["notes"]).classes("text-sm text-gray-700")
                with ui.row().classes("gap-2"):
                    if s["status"] != "Completed" and can_edit:
                        success_button(
                            "Mark as Completed",
                            on_click=lambda: do_mark_completed(s["id"]),
                        )
                    if can_edit:
                        ghost_button("Edit", on_click=lambda: show_form(s))
                    if can_delete:
                        danger_button("Delete", on_click=lambda: del_schedule(s["id"]))
                    ghost_button("Back", on_click=show_empty_detail)

    def do_mark_completed(schedule_id):
        mark_maintenance_completed(schedule_id)
        notify_success("Schedule marked as completed.")
        refresh_list()
        view_schedule(schedule_id)

    def show_form(data=None):
        state["editing_id"] = data["id"] if data else None
        detail_panel.clear()
        clients = get_all_clients()
        client_opts = {c["id"]: c["name"] for c in clients}

        with detail_panel:
            with card():
                ui.label("Edit Schedule" if data else "New Schedule").classes("text-lg font-bold mb-3")

                ui.label("Client").classes(TEXT_LABEL)
                client_sel = (
                    ui.select(client_opts, with_input=True)
                    .props("outlined dense")
                    .classes(INPUT)
                )
                services = get_all_services()
                service_names = sorted(set(s["name"] for s in services))
                ui.label("Service Name").classes(TEXT_LABEL)
                service_name = (
                    ui.select(service_names, with_input=True, new_value_mode="add")
                    .props("outlined dense")
                    .classes(INPUT)
                )
                frequency = labeled_select("Frequency", FREQUENCY_OPTIONS, with_input=False)
                ui.label("Start Date").classes(TEXT_LABEL)
                start_date = (
                    ui.input(placeholder="YYYY-MM-DD")
                    .props("outlined dense type=date")
                    .classes(INPUT)
                )
                ui.label("Next Due Date").classes(TEXT_LABEL)
                next_due = (
                    ui.input(placeholder="YYYY-MM-DD")
                    .props("outlined dense type=date")
                    .classes(INPUT)
                )
                status = labeled_select("Status", STATUS_OPTIONS, with_input=False)
                notes = labeled_textarea("Notes")

                def sync_due_field():
                    next_due.value = _compute_next_due(
                        start_date.value or "", frequency.value or "Once"
                    )
                    if (frequency.value or "Once") == "Once":
                        next_due.disable()
                    else:
                        next_due.enable()

                frequency.on_value_change(lambda _: sync_due_field())
                start_date.on_value_change(lambda _: sync_due_field())

                if data:
                    client_sel.value = data["client_id"]
                    service_name.value = data["service_name"]
                    frequency.value = data["frequency"]
                    start_date.value = data["start_date"]
                    next_due.value = data.get("next_due_date") or ""
                    status.value = data["status"]
                    notes.value = data.get("notes", "") or ""
                    if data.get("frequency") == "Once":
                        sync_due_field()
                    elif data.get("next_due_date"):
                        next_due.enable()
                else:
                    frequency.value = "Once"
                    start_date.value = date.today().isoformat()
                    status.value = "Active"
                    sync_due_field()

                def save():
                    cid = client_sel.value
                    sn = (service_name.value or "").strip()
                    freq = frequency.value or "Once"
                    sd = (start_date.value or "").strip()
                    nd = (next_due.value or "").strip()
                    st = status.value or "Active"
                    nt = (notes.value or "").strip()

                    if not cid:
                        notify_warning("Please select a client.")
                        return
                    if not sn:
                        notify_warning("Service name is required.")
                        return
                    if not sd:
                        notify_warning("Start date is required.")
                        return
                    if not nd and freq != "Once":
                        notify_warning("Next due date is required.")
                        return
                    if not nd and freq == "Once":
                        nd = sd

                    if state["editing_id"]:
                        update_maintenance_schedule(
                            state["editing_id"], cid, sn, freq, sd, nd, st, nt
                        )
                        notify_success("Schedule updated.")
                        refresh_list()
                        view_schedule(state["editing_id"])
                    else:
                        create_maintenance_schedule(cid, sn, freq, sd, nd, st, nt)
                        notify_success("Schedule created.")
                        refresh_list()
                        show_empty_detail()

                with form_actions_row():
                    success_button("Save", on_click=save)
                    ghost_button("Cancel", on_click=show_empty_detail)

    def del_schedule(schedule_id):
        def do_delete():
            delete_maintenance_schedule(schedule_id)
            notify_success("Schedule deleted.")
            refresh_list()
            show_empty_detail()

        confirm_dialog("Delete Schedule", "Delete this maintenance schedule?", do_delete)

    content = page_shell("Maintenance Schedule", wide=True)
    with content:
        search = (
            ui.input(placeholder="Search schedules...")
            .props("outlined dense")
            .classes(f"{INPUT} shrink-0")
        )
        search.on_value_change(
            lambda e: (state.update(search=e.value or ""), refresh_list())
        )
        if user.has_permission("Maintenance_Edit"):
            toolbar(search, add_label="New Schedule", on_add=lambda: show_form())
        else:
            toolbar(search)

        list_panel, detail_panel = split_panels()
        refresh_list()
        show_empty_detail()
