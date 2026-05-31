"""NiceGUI theme and layout helpers (UI Style Guidelines, iOS glossy aesthetic)."""

from contextlib import contextmanager
from pathlib import Path

from nicegui import ui

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

from store_config import LEGACY_LOGO_FILENAME, STORE_LOGO_FILENAME

_logo_path = ASSETS_DIR / STORE_LOGO_FILENAME
if not _logo_path.is_file():
    _logo_path = ASSETS_DIR / LEGACY_LOGO_FILENAME
LOGO_URL = f"/assets/{_logo_path.name}"

PRIMARY = "#3b82f6"
SUCCESS = "#10b981"
BACKGROUND = "#f2f2f7"

# Typography (SF Pro / system stack applied via global CSS)
TEXT_TITLE = "text-2xl font-bold text-slate-900 tracking-tight w-full shrink-0"
TEXT_HEADING = "text-lg font-semibold text-slate-900 tracking-tight"
TEXT_SUBHEADING = "text-base font-semibold text-slate-800"
TEXT_LABEL = "text-sm font-medium text-slate-600 w-full"
TEXT_BODY = "text-sm text-slate-600"
TEXT_MUTED = "text-sm text-slate-500"
TEXT_CAPTION = "text-xs text-slate-500"
TEXT_BRAND = "text-xl font-bold tracking-tight"
TEXT_BRAND_HERO = "text-4xl font-bold tracking-tight"
BRAND_ACCENT = f"text-[{PRIMARY}]"

PAGE_COLUMN = "max-w-4xl mx-auto w-full p-4"
PAGE_WIDE = "max-w-6xl mx-auto w-full p-4"
PAGE_SHELL = "w-full flex-1 min-h-0 h-full flex flex-col gap-4 overflow-hidden"
PAGE_CONTENT = "w-full flex-1 min-h-0 flex flex-col gap-4 overflow-hidden"
SCROLL_PANEL = "w-full overflow-y-auto overflow-x-hidden mega-page-scroll"
PANEL_OUTER = "min-h-0 min-w-0 w-full flex flex-col"
PANEL_SCROLL = f"{SCROLL_PANEL} w-full"
PAGE_BODY_SCROLL_HEIGHT = "height: calc(100dvh - 11rem); max-height: calc(100dvh - 11rem);"
SPLIT_PANEL_HEIGHT = "height: calc(100dvh - 14rem); max-height: calc(100dvh - 14rem);"
SPLIT_GRID = (
    "mega-split-grid w-full gap-4 grid grid-cols-1 lg:grid-cols-12 items-start"
)
FORM_ACTIONS = (
    "gap-2 mt-2 pt-3 shrink-0 w-full border-t border-slate-200/60"
)
CARD = (
    "rounded-2xl border border-white/70 shadow-[0_4px_24px_rgba(15,23,42,0.06)] "
    "bg-white/75 backdrop-blur-xl w-full"
)
CARD_HOVER = (
    f"{CARD} hover:shadow-[0_8px_32px_rgba(15,23,42,0.1)] "
    "hover:bg-white/85 transition-all duration-300 ease-out"
)
BTN = (
    "px-6 py-2 rounded-full border shadow-[0_1px_3px_rgba(15,23,42,0.08),"
    "inset_0_1px_0_rgba(255,255,255,0.45)] backdrop-blur-md "
    "transition-all duration-200 active:scale-[0.98]"
)
BTN_PRIMARY = (
    f"{BTN} bg-gradient-to-b from-blue-400/95 to-blue-600/95 text-white "
    "border-blue-300/40 hover:from-blue-400 hover:to-blue-600 "
    "hover:shadow-[0_4px_14px_rgba(59,130,246,0.35)]"
)
BTN_SUCCESS = (
    f"{BTN} bg-gradient-to-b from-emerald-400/95 to-emerald-600/95 text-white "
    "border-emerald-300/40 hover:from-emerald-400 hover:to-emerald-600 "
    "hover:shadow-[0_4px_14px_rgba(16,185,129,0.35)]"
)
BTN_GHOST = (
    f"{BTN} bg-white/70 text-slate-700 border-white/80 "
    "hover:bg-white/90 hover:shadow-[0_4px_12px_rgba(15,23,42,0.08)]"
)
BTN_DANGER = (
    f"{BTN} bg-gradient-to-b from-red-400/95 to-red-600/95 text-white "
    "border-red-300/40 hover:from-red-400 hover:to-red-600 "
    "hover:shadow-[0_4px_14px_rgba(239,68,68,0.3)]"
)
NAV_ACTIVE = (
    "px-4 py-2 rounded-xl font-semibold text-blue-700 "
    "bg-blue-500/15 border border-blue-400/30 "
    "shadow-[inset_0_1px_0_rgba(255,255,255,0.6)] backdrop-blur-md"
)
NAV_INACTIVE = (
    "px-4 py-2 rounded-xl text-slate-600 border border-transparent "
    "hover:bg-white/55 hover:text-slate-800 backdrop-blur-sm "
    "transition-all duration-200"
)
SIDEBAR = (
    "w-56 shrink-0 h-full bg-white/65 border-r border-white/80 "
    "shadow-[4px_0_24px_rgba(15,23,42,0.04)] backdrop-blur-2xl "
    "flex flex-col min-h-0 overflow-hidden"
)
SIDEBAR_HEADER = "shrink-0 px-4 py-4 gap-0 border-b border-slate-200/50 w-full items-start"
BRAND_LOGO_HERO = (
    "mega-brand-logo mega-brand-logo--hero w-full max-w-[240px] sm:max-w-[280px] "
    "h-auto object-contain mx-auto"
)
BRAND_LOGO_SIDEBAR = (
    "mega-brand-logo mega-brand-logo--sidebar w-full max-w-[168px] "
    "h-auto object-contain object-left"
)
MAIN_PANE = "flex-1 min-w-0 min-h-0 h-full flex flex-col overflow-hidden bg-[#f2f2f7]/50"
MAIN_VIEW_HOST = "w-full flex-1 min-h-0 overflow-hidden flex flex-col"
MAIN_VIEW_SHELL = "mega-main-view w-full flex-1 min-h-0 h-full flex flex-col overflow-hidden"
VIEW_TRANSITION_MS = 320
APP_SHELL = "w-full h-full min-h-0 flex flex-col overflow-hidden"
APP_BODY = "flex-1 min-h-0 w-full flex overflow-hidden grow"
APP_FOOTER = (
    "w-full flex-none shrink-0 px-4 py-2.5 items-center justify-between "
    "text-sm text-slate-500 bg-white/70 border-t border-slate-200/60 "
    "backdrop-blur-xl z-10"
)
SIDEBAR_ACTIVE = (
    "w-full justify-start gap-3 px-3 py-2.5 rounded-xl font-semibold "
    "text-blue-700 bg-blue-500/15 border border-blue-400/30 "
    "shadow-[inset_0_1px_0_rgba(255,255,255,0.55)] backdrop-blur-md"
)
SIDEBAR_INACTIVE = (
    "w-full justify-start gap-3 px-3 py-2.5 rounded-xl text-slate-600 "
    "border border-transparent hover:bg-white/50 hover:text-slate-800 "
    "backdrop-blur-sm transition-all duration-200"
)
SIDEBAR_USER = (
    "w-full px-3 py-3 border-t border-slate-200/50 cursor-pointer "
    "hover:bg-white/45 transition-colors duration-200"
)
USER_MENU = (
    "min-w-[260px] rounded-2xl overflow-hidden "
    "shadow-[0_12px_40px_rgba(15,23,42,0.14)] border border-white/80 "
    "bg-white/90 backdrop-blur-2xl"
)
USER_MENU_HEADER = "px-4 py-3 gap-0.5 border-b border-slate-200/60 w-full"
USER_MENU_LOGOUT = "text-red-500 font-medium"
TAB_ACTIVE = NAV_ACTIVE
TAB_INACTIVE = (
    "px-6 py-2 rounded-xl text-slate-600 border border-transparent "
    "bg-white/45 hover:bg-white/65 backdrop-blur-sm transition-all duration-200"
)
INPUT = "w-full ios-field"
BTN_PROPS = "unelevated dense no-caps"
LIST_ROW = "w-full items-center gap-2 flex-wrap border-b border-slate-200/40 pb-2"

_GLOBAL_STYLES_APPLIED = False

_IOS_GLOBAL_CSS = """
:root {
  --ios-primary: #3b82f6;
  --ios-success: #10b981;
  --ios-bg: #f2f2f7;
}
html, body, .nicegui-content {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display",
    "Helvetica Neue", "Segoe UI", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.q-field--outlined .q-field__control,
.q-field--filled .q-field__control {
  border-radius: 12px !important;
  background: rgba(255, 255, 255, 0.82) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7),
    0 1px 2px rgba(15, 23, 42, 0.04);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.q-field--outlined .q-field__control:before {
  border-color: rgba(148, 163, 184, 0.45) !important;
}
.q-field--focused .q-field__control:before {
  border-color: var(--ios-primary) !important;
  border-width: 2px !important;
}
.q-field__label, .q-field__native, .q-field__input {
  color: #334155 !important;
  font-weight: 500;
}
.q-field__label {
  font-size: 0.8125rem;
}
.q-btn {
  font-weight: 600 !important;
  letter-spacing: -0.01em;
}
.q-menu {
  border-radius: 16px !important;
  overflow: hidden;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}
.q-item {
  min-height: 44px;
  border-radius: 10px;
  margin: 2px 6px;
  font-weight: 500;
}
.q-item:hover {
  background: rgba(59, 130, 246, 0.08) !important;
}
.q-dialog .q-card {
  border-radius: 20px !important;
  background: rgba(255, 255, 255, 0.92) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.15) !important;
}
.q-scrollarea__thumb {
  background: rgba(148, 163, 184, 0.45) !important;
  border-radius: 999px !important;
  opacity: 0.85;
}
.mega-page-scroll.q-scrollarea .q-scrollarea__bar--v {
  opacity: 1 !important;
  width: 8px;
}
.q-badge {
  border-radius: 999px !important;
  font-weight: 600;
  padding: 2px 8px;
}
.q-notification {
  border-radius: 14px !important;
  backdrop-filter: blur(16px);
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.12) !important;
}
.q-avatar {
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
}
/* macOS / iOS–style main content transitions (sidebar navigation) */
.mega-main-view {
  will-change: transform, opacity;
  transform-origin: center top;
}
.view-enter-forward {
  animation: megaViewEnterForward 0.42s cubic-bezier(0.32, 0.72, 0, 1) both;
}
.view-enter-back {
  animation: megaViewEnterBack 0.42s cubic-bezier(0.32, 0.72, 0, 1) both;
}
.view-exit-forward {
  animation: megaViewExitForward 0.28s cubic-bezier(0.32, 0.72, 0, 1) forwards;
  pointer-events: none;
}
.view-exit-back {
  animation: megaViewExitBack 0.28s cubic-bezier(0.32, 0.72, 0, 1) forwards;
  pointer-events: none;
}
@keyframes megaViewEnterForward {
  from {
    opacity: 0;
    transform: translate3d(32px, 6px, 0) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
  }
}
@keyframes megaViewEnterBack {
  from {
    opacity: 0;
    transform: translate3d(-32px, 6px, 0) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
  }
}
@keyframes megaViewExitForward {
  from {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
  }
  to {
    opacity: 0;
    transform: translate3d(-24px, 0, 0) scale(0.99);
  }
}
@keyframes megaViewExitBack {
  from {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
  }
  to {
    opacity: 0;
    transform: translate3d(24px, 0, 0) scale(0.99);
  }
}
@media (prefers-reduced-motion: reduce) {
  .mega-main-view.view-enter-forward,
  .mega-main-view.view-enter-back,
  .mega-main-view.view-exit-forward,
  .mega-main-view.view-exit-back {
    animation: none !important;
  }
}
.mega-brand-logo {
  display: block;
  flex-shrink: 0;
}
.mega-brand-logo--hero {
  max-height: min(28vw, 160px);
}
.mega-brand-logo--sidebar {
  max-height: 72px;
}
@media (max-width: 640px) {
  .mega-brand-logo--hero {
    max-height: 120px;
  }
}
/* Dashboard stat groups */
.mega-stat-group {
  padding: 0 !important;
  overflow: hidden;
}
.mega-stat-group-header {
  display: flex;
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  font: inherit;
  padding: 0;
  -webkit-tap-highlight-color: transparent;
  transition: background-color 0.2s ease;
}
.mega-stat-group-body {
  overflow: hidden;
  max-height: 0;
  opacity: 0;
  transition: max-height 0.35s cubic-bezier(0.32, 0.72, 0, 1),
    opacity 0.25s ease;
}
.mega-stat-group.is-open .mega-stat-group-body {
  max-height: 720px;
  opacity: 1;
}
.mega-stat-group-inner {
  overflow: hidden;
}
@media (prefers-reduced-motion: reduce) {
  .mega-stat-group-body {
    transition: none !important;
  }
}
/* Page scroll — always-visible scrollbar for desktop UX */
.mega-page-scroll {
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: rgba(100, 116, 139, 0.55) transparent;
}
.mega-page-scroll::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
.mega-page-scroll::-webkit-scrollbar-track {
  background: rgba(148, 163, 184, 0.08);
  border-radius: 999px;
}
.mega-page-scroll::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.55);
  border-radius: 999px;
  border: 2px solid transparent;
  background-clip: padding-box;
}
.mega-page-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(71, 85, 105, 0.75);
  background-clip: padding-box;
  border: 2px solid transparent;
}
/* Master/detail grid — let each panel size from its own explicit height */
.mega-split-grid {
  align-items: start;
}
"""


def _apply_global_styles():
    global _GLOBAL_STYLES_APPLIED
    if _GLOBAL_STYLES_APPLIED:
        return
    ui.add_css(_IOS_GLOBAL_CSS)
    _GLOBAL_STYLES_APPLIED = True


def brand_logo(*, variant: str = "hero"):
    """Responsive MEGAA Electronics logo. variant: 'hero' (login) or 'sidebar' (app shell)."""
    classes = BRAND_LOGO_HERO if variant == "hero" else BRAND_LOGO_SIDEBAR
    return ui.image(LOGO_URL).props("no-spinner").classes(classes)


def apply_page_background(*, lock_viewport: bool = False):
    """Apply page background; lock viewport to prevent document scroll on app shell."""
    _apply_global_styles()
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
        ui.label(title).classes(TEXT_TITLE)
        content = ui.column().classes(PAGE_CONTENT)
    return content


@contextmanager
def page_scroll_body():
    """Scrollable page body for single-column layouts (e.g. dashboard)."""
    with ui.column().classes(
        "w-full overflow-y-auto overflow-x-hidden gap-4 mega-page-scroll pr-1 pb-4"
    ).style(PAGE_BODY_SCROLL_HEIGHT):
        yield


def form_actions_row():
    """Save/Cancel row inside a form card."""
    return ui.row().classes(f"gap-2 mt-4 pt-3 w-full border-t border-slate-200/60")


def card(interactive: bool = False):
    base = CARD_HOVER if interactive else CARD
    return ui.card().classes(f"{base} p-4")


def labeled_input(label: str, *, password: bool = False, placeholder: str = ""):
    ui.label(label).classes(TEXT_LABEL)
    props = "outlined dense"
    if password:
        inp = ui.input(placeholder=placeholder, password=True, password_toggle_button=True).props(props)
    else:
        inp = ui.input(placeholder=placeholder).props(props)
    inp.classes(INPUT)
    return inp


def labeled_select(label: str, options: list, *, with_input: bool = True):
    ui.label(label).classes(TEXT_LABEL)
    sel = ui.select(options, with_input=with_input).props("outlined dense").classes(INPUT)
    return sel


def labeled_textarea(label: str, *, rows: int = 3):
    ui.label(label).classes(TEXT_LABEL)
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


def nav_view_direction(previous: str, target: str, order: list[str]) -> str:
    """Return 'forward' or 'back' for iOS-style horizontal content transitions."""
    try:
        prev_i = order.index(previous)
        next_i = order.index(target)
    except ValueError:
        return "forward"
    if next_i > prev_i:
        return "forward"
    if next_i < prev_i:
        return "back"
    return "forward"


def trigger_main_view_exit(direction: str) -> None:
    """Animate the current main pane out before it is cleared."""
    ui.run_javascript(
        f"""
        () => {{
            const pane = document.querySelector('.mega-main-view');
            if (!pane) return;
            pane.classList.remove(
                'view-enter-forward', 'view-enter-back',
                'view-exit-forward', 'view-exit-back'
            );
            pane.classList.add('view-exit-{direction}');
        }}
        """
    )


def sidebar_user_menu(
    *,
    display_name: str,
    username: str,
    subtitle: str,
    on_password,
    on_logout,
):
    """Account trigger at the bottom of the sidebar with a frosted popover menu."""
    with ui.button().props("flat no-caps align=left").classes(f"{SIDEBAR_USER} w-full"):
        with ui.row().classes("w-full items-center gap-3 no-wrap"):
            ui.avatar(icon="person", color="primary").classes("shrink-0")
            with ui.column().classes("gap-0 min-w-0 flex-grow text-left"):
                ui.label(display_name).classes(
                    f"text-sm font-semibold text-slate-800 truncate w-full"
                )
                ui.label(subtitle).classes(f"{TEXT_CAPTION} truncate w-full")

        with ui.menu().props('anchor="top right" self="bottom left"').classes(USER_MENU):
            with ui.column().classes(USER_MENU_HEADER):
                ui.label("Personal Settings").classes(TEXT_SUBHEADING)
                ui.label(display_name).classes(f"{TEXT_CAPTION} truncate w-full")
                ui.label(f"@{username}").classes("text-xs text-slate-400 truncate w-full")

            ui.menu_item("Log Out", on_click=on_logout).props(
                "icon=logout"
            ).classes(USER_MENU_LOGOUT)
            ui.menu_item("Change Password", on_click=on_password).props("icon=lock")


def toolbar(search_input, *, add_label: str | None = None, on_add=None):
    with ui.row().classes("w-full gap-3 items-center flex-wrap shrink-0") as row:
        search_input.move(row)
        search_input.classes(remove="w-full shrink-0")
        search_input.classes("flex-1 min-w-[200px]")
        if add_label and on_add:
            success_button(add_label, on_click=on_add)


def split_panels(*, list_cols: str = "lg:col-span-5", detail_cols: str = "lg:col-span-7", panel_height: str = ""):
    """Master/detail columns; each side scrolls independently when content overflows."""
    height_style = panel_height if panel_height else SPLIT_PANEL_HEIGHT
    with ui.grid().classes(SPLIT_GRID):
        with ui.column().classes(f"{list_cols} {PANEL_OUTER}"):
            with ui.column().classes(PANEL_SCROLL).style(height_style):
                list_panel = ui.column().classes("w-full min-w-0 gap-4 pr-1 pb-4")
        with ui.column().classes(f"{detail_cols} {PANEL_OUTER}"):
            with ui.column().classes(PANEL_SCROLL).style(height_style):
                detail_panel = ui.column().classes("w-full min-w-0 gap-4 pr-1 pb-4")
    return list_panel, detail_panel


def show_pdf_in_detail_panel(
    panel,
    *,
    pdf_url: str,
    title: str,
    subtitle: str = "",
    on_back=None,
    on_whatsapp=None,
):
    """Render a PDF preview in the master/detail right pane."""
    panel.clear()
    with panel:
        with ui.column().classes("w-full min-h-0 gap-3"):
            with ui.row().classes("w-full items-start justify-between gap-2 flex-wrap shrink-0"):
                with ui.column().classes("gap-0 min-w-0"):
                    ui.label(title).classes(TEXT_HEADING)
                    if subtitle:
                        ui.label(subtitle).classes(TEXT_CAPTION)
                with ui.row().classes("gap-2 shrink-0"):
                    if on_whatsapp:
                        ghost_button("Send to Whatsapp", on_click=on_whatsapp)
                    if on_back:
                        ghost_button("Back", on_click=on_back)
            (
                ui.element("iframe")
                .props(f'src="{pdf_url}" title="{title}"')
                .classes(
                    "w-full border-0 rounded-xl bg-white "
                    "shadow-[inset_0_0_0_1px_rgba(15,23,42,0.08)]"
                )
                .style("height: calc(100dvh - 16rem); min-height: 360px; max-height: calc(100dvh - 16rem);")
            )


def stat_cards_grid():
    return ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4")


@contextmanager
def collapsible_stat_group(
    title: str,
    summary: str = "",
    *,
    caption: str = "",
    default_open: bool = True,
):
    """Dashboard stat section with a static header."""
    _apply_global_styles()
    group_classes = f"mega-stat-group is-open {CARD}"

    with ui.element("div").classes(group_classes):
        with ui.element("div").classes(
            "w-full flex items-center gap-3 px-4 py-3"
        ):
            with ui.column().classes("items-start gap-0.5 min-w-0 text-left"):
                ui.label(title).classes(TEXT_SUBHEADING)
                if summary:
                    ui.label(summary).classes(
                        "text-base font-bold text-slate-900 tracking-tight"
                    )
                if caption:
                    ui.label(caption).classes(TEXT_CAPTION)

        with ui.element("div").classes("mega-stat-group-body"):
            with ui.element("div").classes("mega-stat-group-inner"):
                with ui.column().classes("w-full gap-4 px-4 pb-4 pt-1") as content:
                    yield content


def stat_card(title: str, value: str, accent: str = PRIMARY, subtitle: str = ""):
    with ui.card().classes(f"{CARD} p-4 w-full"):
        with ui.row().classes("w-full items-stretch gap-3"):
            ui.element("div").classes("w-1.5 rounded-full shadow-sm").style(f"background:{accent}")
            with ui.column().classes("gap-1"):
                ui.label(title).classes(TEXT_CAPTION)
                ui.label(value).classes("text-xl font-bold text-slate-900 tracking-tight")
                if subtitle:
                    ui.label(subtitle).classes("text-xs text-gray-500")


def empty_state(message: str):
    ui.label(message).classes(f"{TEXT_MUTED} text-center w-full py-8")


def confirm_dialog(title: str, message: str, on_confirm):
    with ui.dialog() as dialog, ui.card().classes(f"{CARD} p-4"):
        ui.label(title).classes(TEXT_HEADING)
        ui.label(message).classes(TEXT_BODY)
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
