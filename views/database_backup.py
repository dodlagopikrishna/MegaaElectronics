import asyncio

from nicegui import ui

from database_backup import get_backup_dir, get_last_backup_info, run_folder_backup
from database_setup import DB_PATH
from login_manager import CurrentUser
from ui_theme import (
    card,
    notify_success,
    notify_warning,
    page_scroll_body,
    page_shell,
    success_button,
    TEXT_BODY,
    TEXT_CAPTION,
    TEXT_MUTED,
)


def render_database_backup():
    user = CurrentUser.get()
    if not user.has_permission("Database_Backup"):
        content = page_shell("Database Backup", wide=True)
        with content:
            with card():
                ui.label("You do not have permission to back up the database.").classes(TEXT_BODY)
        return

    content = page_shell("Database Backup", wide=True)
    state = {"busy": False}

    def refresh_status(backup_dir_label, last_sync_label, last_file_label):
        backup_dir_label.text = get_backup_dir()
        info = get_last_backup_info()
        last_sync_label.text = info["last_sync"] or "Never"
        last_file_label.text = info["last_file"] or "—"

    with content:
        with page_scroll_body():
            with ui.column().classes("w-full gap-4 max-w-3xl"):
                with card():
                    ui.label("Database backup").classes("text-lg font-bold mb-2")
                    ui.label("Live database path").classes(TEXT_CAPTION)
                    ui.label(DB_PATH).classes(f"{TEXT_BODY} font-mono text-xs break-all mb-3")
                    ui.label("Backup folder").classes(TEXT_CAPTION)
                    backup_dir_label = ui.label("").classes(
                        f"{TEXT_BODY} font-mono text-xs break-all mb-3"
                    )
                    ui.label("Last backup").classes(TEXT_CAPTION)
                    last_sync_label = ui.label("").classes(f"{TEXT_BODY} mb-1")
                    ui.label("Last snapshot").classes(TEXT_CAPTION)
                    last_file_label = ui.label("").classes(f"{TEXT_BODY} mb-3")

                    ui.label(
                        "Each save creates a new timestamped snapshot. Previous snapshots are kept "
                        "and are never overwritten."
                    ).classes(f"{TEXT_MUTED} mb-2")
                    ui.label(
                        "When the app closes, a snapshot is saved automatically."
                    ).classes(f"{TEXT_MUTED} mb-4")

                    status_label = ui.label("").classes("text-sm text-slate-600 min-h-[1.25rem]")

                    async def save_database():
                        if state["busy"]:
                            return
                        state["busy"] = True
                        status_label.text = "Saving database snapshot…"
                        try:
                            result = await asyncio.to_thread(run_folder_backup)
                            if result["success"]:
                                notify_success(result["message"])
                                status_label.text = ""
                            else:
                                notify_warning(result["message"])
                                status_label.text = result["message"]
                        except Exception as exc:
                            notify_warning(f"Backup failed: {exc}")
                            status_label.text = str(exc)
                        finally:
                            state["busy"] = False
                            refresh_status(
                                backup_dir_label, last_sync_label, last_file_label
                            )

                    success_button("Save Database", on_click=save_database)

            refresh_status(backup_dir_label, last_sync_label, last_file_label)
