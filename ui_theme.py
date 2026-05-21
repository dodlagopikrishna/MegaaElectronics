"""NiceGUI theme and layout helpers (UI Style Guidelines)."""

from contextlib import contextmanager

from nicegui import ui

PRIMARY = "#3b82f6"
SUCCESS = "#10b981"
BACKGROUND = "#f8fafc"

PAGE_COLUMN = "max-w-4xl mx-auto w-full p-4"
PAGE_WIDE = "max-w-6xl mx-auto w-full p-4"
PAGE_SHELL = "w-full flex-1 min-h-0 h-full flex flex-col gap-4"
PAGE_CONTENT = "w-full flex-1 min-h-0 flex flex-col gap-4 min-h-0"
SCROLL_PANEL = "w-full min-h-0 overflow-y-auto overflow-x-hidden"
PANEL_OUTER = "min-h-0 h-full w-full flex flex-col overflow-hidden"
# Fits content below app chrome (title, toolbar, footer); leaves room for action buttons.
SCROLL_VIEWPORT = "height: calc(100dvh - 10.5rem); max-height: calc(100dvh - 10.5rem); width: 100%;"
SPLIT_GRID = (
    "w-full flex-1 min-h-0 gap-4 grid grid-cols-1 lg:grid-cols-12 "
    "grid-rows-1 items-stretch min-h-0"
)
FORM_ACTIONS = "gap-2 mt-2 pt-3 shrink-0 w-full border-t border-gray-200"
CARD = "rounded-xl border border-gray-200 shadow-sm bg-white w-full"
CARD_HOVER = (
    "rounded-xl border border-gray-200 shadow-sm bg-white w-full "
    "hover:shadow-md transition-all duration-200"
)
BTN = "px-6 py-2 rounded-lg border shadow-sm backdrop-blur-md transition-all duration-200"
BTN_PRIMARY = (
    f"{BTN} bg-blue-500/80 text-white border-blue-300/50 "
    "hover:bg-blue-500/90 hover:shadow-md"
)
BTN_SUCCESS = (
    f"{BTN} bg-emerald-500/75 text-white border-emerald-300/50 "
    "hover:bg-emerald-500/90 hover:shadow-md"
)
BTN_GHOST = (
    f"{BTN} bg-white/55 text-gray-700 border-white/70 "
    "hover:bg-white/75 hover:shadow-md"
)
BTN_DANGER = (
    f"{BTN} bg-red-500/75 text-white border-red-300/50 "
    "hover:bg-red-500/90 hover:shadow-md"
)
NAV_ACTIVE = (
    "px-4 py-2 rounded-lg font-semibold "
    "bg-blue-500/25 text-blue-700 border border-blue-400/50 "
    "backdrop-blur-md shadow-sm"
)
NAV_INACTIVE = (
    "px-4 py-2 rounded-lg text-gray-600 border border-transparent "
    "hover:bg-white/50 hover:text-gray-800 backdrop-blur-sm transition-all duration-200"
)
SIDEBAR = (
    "w-56 shrink-0 h-full bg-white border-r border-gray-200 shadow-sm "
    "flex flex-col min-h-0 overflow-hidden"
)
MAIN_PANE = "flex-1 min-w-0 min-h-0 h-full flex flex-col overflow-hidden"
MAIN_SCROLL = "w-full flex-1 min-h-0 overflow-y-auto overflow-x-hidden"
APP_SHELL = "w-full h-full min-h-0 flex flex-col overflow-hidden"
APP_BODY = "flex-1 min-h-0 w-full flex overflow-hidden grow"
APP_FOOTER = (
    "w-full flex-none shrink-0 px-4 py-2.5 items-center justify-between "
    "text-sm text-gray-500 bg-white border-t border-gray-200 z-10"
)
SIDEBAR_ACTIVE = (
    "w-full justify-start gap-3 px-3 py-2.5 rounded-lg font-semibold "
    "bg-blue-500/25 text-blue-700 border border-blue-400/50 "
    "backdrop-blur-md shadow-sm"
)
SIDEBAR_INACTIVE = (
    "w-full justify-start gap-3 px-3 py-2.5 rounded-lg text-gray-600 "
    "border border-transparent hover:bg-white/50 hover:text-gray-800 "
    "backdrop-blur-sm transition-all duration-200"
)
SIDEBAR_USER = (
    "w-full px-3 py-3 border-t border-gray-200 cursor-pointer "
    "hover:bg-gray-50 transition-colors duration-200"
)
USER_MENU = "min-w-[240px] shadow-xl"
USER_MENU_LOGOUT = "text-red-400 font-medium"
TAB_ACTIVE = NAV_ACTIVE
TAB_INACTIVE = (
    "px-6 py-2 rounded-lg text-gray-600 border border-transparent "
    "bg-white/40 hover:bg-white/60 backdrop-blur-sm transition-all duration-200"
)
INPUT = "w-full"
BTN_PROPS = "unelevated dense no-caps"


def apply_page_background(*, lock_viewport: bool = False):
    """Apply page background; lock viewport to prevent document scroll on app shell."""
    base = f"bg-[{BACKGROUND}] m-0"
    if lock_viewport:
        ui.query("html").classes("h-full min-h-0 overflow-hidden")
        ui.query("body").classes(f"{base} h-full min-h-0 overflow-hidden")
        ui.query(".nicegui-content").classes(
            "h-full min-h-0 overflow-hidden flex flex-col"
        )
    else:
        ui.query("body").classes(f"{base} min-h-screen")


def page_shell(title: str, *, wide: bool = False):
    """Page title + flex body; pair with split_panels or page_scroll_body()."""
    col_classes = PAGE_WIDE if wide else PAGE_COLUMN
    with ui.column().classes(f"{col_classes} {PAGE_SHELL}"):
        ui.label(title).classes("text-2xl font-bold text-gray-800 w-full shrink-0")
        content = ui.column().classes(PAGE_CONTENT)
    return content


@contextmanager
def page_scroll_body():
    """Scrollable page body for single-column layouts (e.g. dashboard)."""
    scroll = ui.scroll_area().classes("w-full flex-1 min-h-0").props("visible")
    scroll.style(SCROLL_VIEWPORT)
    with scroll:
        body = ui.column().classes("w-full gap-4")
        yield body


def form_actions_row():
    """Save/Cancel row inside a form card."""
    return ui.row().classes("gap-2 mt-4 pt-3 w-full border-t border-gray-200")


def card(interactive: bool = False):
    base = CARD_HOVER if interactive else CARD
    return ui.card().classes(f"{base} p-4")


def labeled_input(label: str, *, password: bool = False, placeholder: str = ""):
    ui.label(label).classes("text-sm font-medium text-gray-700 w-full")
    props = "outlined dense"
    if password:
        inp = ui.input(placeholder=placeholder, password=True, password_toggle_button=True).props(props)
    else:
        inp = ui.input(placeholder=placeholder).props(props)
    inp.classes(INPUT)
    return inp


def labeled_select(label: str, options: list, *, with_input: bool = True):
    ui.label(label).classes("text-sm font-medium text-gray-700 w-full")
    sel = ui.select(options, with_input=with_input).props("outlined dense").classes(INPUT)
    return sel


def labeled_textarea(label: str, *, rows: int = 3):
    ui.label(label).classes("text-sm font-medium text-gray-700 w-full")
    ta = ui.textarea().props(f"outlined dense rows={rows}").classes(INPUT)
    return ta


def _glass_button(text: str, classes: str, on_click=None):
    return ui.button(text, on_click=on_click).props(BTN_PROPS).classes(classes)


def primary_button(text: str, on_click=None):
    return _glass_button(text, BTN_PRIMARY, on_click)


def success_button(text: str, on_click=None):
    return _glass_button(text, BTN_SUCCESS, on_click)


def ghost_button(text: str, on_click=None):
    return _glass_button(text, BTN_GHOST, on_click)


def danger_button(text: str, on_click=None):
    return _glass_button(text, BTN_DANGER, on_click)


def nav_button(text: str, on_click=None):
    return ui.button(text, on_click=on_click).props(BTN_PROPS).classes(NAV_INACTIVE)


def sidebar_nav_button(text: str, icon: str, on_click=None):
    return (
        ui.button(text, icon=icon, on_click=on_click)
        .props(f"{BTN_PROPS} align=left")
        .classes(SIDEBAR_INACTIVE)
    )


def set_nav_active(btn, *, active: bool):
    btn.classes(replace=NAV_ACTIVE if active else NAV_INACTIVE)


def set_sidebar_nav_active(btn, *, active: bool):
    btn.classes(replace=SIDEBAR_ACTIVE if active else SIDEBAR_INACTIVE)


def sidebar_user_menu(
    *,
    display_name: str,
    username: str,
    subtitle: str,
    on_password,
    on_logout,
):
    """Datadog-style account trigger at the bottom of the sidebar with a popover menu."""
    with ui.button().props("flat no-caps align=left").classes(f"{SIDEBAR_USER} w-full"):
        with ui.row().classes("w-full items-center gap-3 no-wrap"):
            ui.avatar(icon="person", color="primary").classes("shrink-0")
            with ui.column().classes("gap-0 min-w-0 flex-grow text-left"):
                ui.label(display_name).classes(
                    "text-sm font-semibold text-gray-800 truncate w-full"
                )
                ui.label(subtitle).classes("text-xs text-gray-500 truncate w-full")

        with ui.menu().props(
            'dark anchor="top right" self="bottom left"'
        ).classes(USER_MENU):
            with ui.column().classes("px-4 py-3 gap-0.5 border-b border-gray-600 w-full"):
                ui.label("Personal Settings").classes("text-sm font-bold")
                ui.label(display_name).classes("text-xs text-gray-300 truncate w-full")
                ui.label(f"@{username}").classes("text-xs text-gray-400 truncate w-full")

            ui.menu_item("Log Out", on_click=on_logout).props(
                "icon=logout"
            ).classes(USER_MENU_LOGOUT)
            ui.menu_item("Change Password", on_click=on_password).props("icon=lock")


def toolbar(search_input, *, add_label: str | None = None, on_add=None):
    with ui.row().classes("w-full gap-3 items-center flex-wrap shrink-0"):
        search_input.classes("flex-grow")
        if add_label and on_add:
            success_button(add_label, on_click=on_add)


def split_panels(*, list_weight: str = "lg:col-span-5", detail_weight: str = "lg:col-span-7"):
    """Master/detail columns; both sides scroll when content overflows."""
    with ui.grid().classes(SPLIT_GRID):
        with ui.column().classes(f"{list_weight} {PANEL_OUTER}"):
            list_scroll = ui.scroll_area().classes("w-full").props("visible")
            list_scroll.style(SCROLL_VIEWPORT)
            with list_scroll:
                list_panel = ui.column().classes("w-full gap-4")
        with ui.column().classes(f"{detail_weight} {PANEL_OUTER}"):
            detail_scroll = ui.scroll_area().classes("w-full").props("visible")
            detail_scroll.style(SCROLL_VIEWPORT)
            with detail_scroll:
                detail_panel = ui.column().classes("w-full gap-4")
    return list_panel, detail_panel


def stat_cards_grid():
    return ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4")


def stat_card(title: str, value: str, accent: str = PRIMARY):
    with ui.card().classes(f"{CARD} p-4 w-full"):
        with ui.row().classes("w-full items-stretch gap-3"):
            ui.element("div").classes("w-1 rounded-full").style(f"background:{accent}")
            with ui.column().classes("gap-1"):
                ui.label(title).classes("text-sm text-gray-500")
                ui.label(value).classes("text-xl font-bold text-gray-800")


def empty_state(message: str):
    ui.label(message).classes("text-gray-500 text-center w-full py-8")


def confirm_dialog(title: str, message: str, on_confirm):
    with ui.dialog() as dialog, ui.card().classes(f"{CARD} p-4"):
        ui.label(title).classes("text-lg font-bold")
        ui.label(message).classes("text-gray-600")
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ghost_button("Cancel", on_click=dialog.close)

            def confirm():
                dialog.close()
                on_confirm()

            danger_button("Confirm", on_click=confirm)
    dialog.open()


def notify_success(message: str):
    ui.notify(message, type="positive")


def notify_warning(message: str):
    ui.notify(message, type="warning")


def notify_error(message: str):
    ui.notify(message, type="negative")
