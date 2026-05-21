"""Shared responsive layout helpers for MEGA Electronics (CustomTkinter)."""

import customtkinter as ctk
import tkinter as tk

# Layout breakpoints (pixels)
SIDEBAR_COLLAPSE_WIDTH = 1000
SPLIT_STACK_WIDTH = 1050
DASHBOARD_CARDS_2COL = 900
DASHBOARD_CARDS_1COL = 520

SIDEBAR_WIDTH_FULL = 220
SIDEBAR_WIDTH_COMPACT = 72

# Login window
LOGIN_MIN_WIDTH = 300
LOGIN_MIN_HEIGHT = 380
LOGIN_DEFAULT_WIDTH = 420
LOGIN_DEFAULT_HEIGHT = 480
LOGIN_PADDING_NARROW = 16
LOGIN_PADDING_WIDE = 48
LOGIN_NARROW_WIDTH = 360

# Side-by-side panels (e.g. tax/notes in quote builder)
SIDE_BY_SIDE_STACK_AT = 420


def canvas_bg():
    return "#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ebebeb"


class DualScrollFrame(ctk.CTkFrame):
    """Scrollable container with vertical and horizontal scrolling for wide tables."""

    def __init__(self, master, corner_radius=12, fg_color=None, **kwargs):
        super().__init__(master, fg_color=fg_color or "transparent", **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(
            self, highlightthickness=0, bd=0, bg=canvas_bg()
        )
        self._v_scroll = ctk.CTkScrollbar(
            self, orientation="vertical", command=self._canvas.yview
        )
        self._h_scroll = ctk.CTkScrollbar(
            self, orientation="horizontal", command=self._canvas.xview
        )

        self.inner = ctk.CTkFrame(self._canvas, fg_color="transparent")
        self._window_id = self._canvas.create_window(
            (0, 0), window=self.inner, anchor="nw"
        )

        self._canvas.configure(
            xscrollcommand=self._h_scroll.set,
            yscrollcommand=self._v_scroll.set,
        )

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._v_scroll.grid(row=0, column=1, sticky="ns")
        self._h_scroll.grid(row=1, column=0, sticky="ew")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        self._min_inner_width = 680

    def update_theme(self):
        self._canvas.configure(bg=canvas_bg())

    def _sync_inner_width(self):
        canvas_w = self._canvas.winfo_width()
        if canvas_w < 2:
            return
        needed = max(self.inner.winfo_reqwidth(), canvas_w, self._min_inner_width)
        self._canvas.itemconfig(self._window_id, width=needed)
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_inner_configure(self, _event=None):
        self._sync_inner_width()

    def _on_canvas_configure(self, _event=None):
        self._sync_inner_width()


def apply_scroll_theme(widget):
    """Update canvas backgrounds after light/dark toggle."""
    if isinstance(widget, DualScrollFrame):
        widget.update_theme()
    for child in widget.winfo_children():
        apply_scroll_theme(child)


class ResponsiveSplitView:
    """Table/list panel + side panel that stacks vertically on narrow widths."""

    def __init__(
        self,
        parent,
        table_weight=3,
        panel_weight=2,
        stack_at=SPLIT_STACK_WIDTH,
        use_dual_scroll=True,
    ):
        self.parent = parent
        self.table_weight = table_weight
        self.panel_weight = panel_weight
        self.stack_at = stack_at
        self._layout_mode = None

        self.content = ctk.CTkFrame(parent, fg_color="transparent")
        self.content.pack(fill="both", expand=True)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        if use_dual_scroll:
            self.table_frame = DualScrollFrame(self.content, corner_radius=12)
            self._table_inner = self.table_frame.inner
        else:
            self.table_frame = ctk.CTkScrollableFrame(self.content, corner_radius=12)
            self._table_inner = self.table_frame

        self.panel_frame = ctk.CTkFrame(self.content, corner_radius=12)

        self.content.bind("<Configure>", self._on_resize, add="+")
        parent.bind("<Configure>", self._on_resize, add="+")

    @property
    def table_inner(self):
        return self._table_inner

    def _on_resize(self, _event=None):
        try:
            if not self.content.winfo_exists():
                return
            width = self.content.winfo_width()
            if width < 2:
                return
            if width < self.stack_at:
                self._apply_stack()
            else:
                self._apply_split()
        except tk.TclError:
            pass

    def _apply_split(self):
        if self._layout_mode == "split":
            return
        self._layout_mode = "split"
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=0)
        self.content.grid_columnconfigure(0, weight=self.table_weight)
        self.content.grid_columnconfigure(1, weight=self.panel_weight)

        self.table_frame.grid(
            row=0, column=0, sticky="nsew", padx=(0, 10), pady=0
        )
        self.panel_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

    def _apply_stack(self):
        if self._layout_mode == "stack":
            return
        self._layout_mode = "stack"
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=0)
        self.content.grid_rowconfigure(0, weight=3)
        self.content.grid_rowconfigure(1, weight=2)

        self.table_frame.grid(
            row=0, column=0, sticky="nsew", padx=0, pady=(0, 10)
        )
        self.panel_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

    def schedule_layout(self):
        self.content.after_idle(self._on_resize)


def build_toolbar(parent, search_var, placeholder, add_text=None, add_command=None, pady=(0, 10)):
    """Search field that grows; optional action button stays on the right."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=20, pady=pady)
    frame.grid_columnconfigure(0, weight=1)

    entry = ctk.CTkEntry(frame, placeholder_text=placeholder, textvariable=search_var)
    entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

    if add_text and add_command:
        ctk.CTkButton(
            frame,
            text=add_text,
            width=120,
            fg_color="#27ae60",
            hover_color="#219a52",
            command=add_command,
        ).grid(row=0, column=1, sticky="e")

    return frame


def render_table_header(parent, columns, weights, header_color="#2980b9"):
    """columns: list of header strings; weights: column weight list."""
    header_row = ctk.CTkFrame(parent, fg_color=header_color, corner_radius=8)
    header_row.pack(fill="x", pady=(0, 2))
    for i, col in enumerate(columns):
        header_row.grid_columnconfigure(i, weight=weights[i], uniform="cols")
        ctk.CTkLabel(
            header_row,
            text=col,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
        ).grid(row=0, column=i, padx=8, pady=6, sticky="ew")

    return header_row


def render_table_row(parent, weights):
    row = ctk.CTkFrame(parent, corner_radius=6)
    row.pack(fill="x", pady=1)
    for i in range(len(weights)):
        row.grid_columnconfigure(i, weight=weights[i], uniform="cols")
    return row


def grid_cell(row, column, text, *, text_color=None, font_size=12):
    kwargs = {"font": ctk.CTkFont(size=font_size)}
    if text_color:
        kwargs["text_color"] = text_color
    lbl = ctk.CTkLabel(row, text=text, **kwargs)
    lbl.grid(row=0, column=column, padx=8, pady=6, sticky="ew")
    return lbl


def grid_actions(row, column, buttons):
    """buttons: list of (text, command, optional kwargs dict)."""
    btn_frame = ctk.CTkFrame(row, fg_color="transparent")
    btn_frame.grid(row=0, column=column, padx=8, pady=4, sticky="ew")
    for text, command, *extra in buttons:
        opts = extra[0] if extra else {}
        defaults = {"width": 50, "height": 26, "font": ctk.CTkFont(size=11)}
        defaults.update(opts)
        ctk.CTkButton(btn_frame, text=text, command=command, **defaults).pack(
            side="left", padx=2
        )
    return btn_frame


class ResponsiveDashboardLayout:
    """Re-flows stat cards and detail panels based on available width."""

    def __init__(self, cards_frame, details_frame):
        self.cards_frame = cards_frame
        self.details_frame = details_frame
        self._card_data = []
        self._cards = []
        self.cards_frame.bind("<Configure>", self._on_cards_resize, add="+")

    def set_cards(self, card_data):
        """card_data: list of (title, value, color)."""
        self._card_data = card_data
        self._rebuild_cards()

    def _on_cards_resize(self, _event=None):
        if not self._card_data:
            return
        w = self.cards_frame.winfo_width()
        if w < 2:
            return
        if w < DASHBOARD_CARDS_1COL:
            cols = 1
        elif w < DASHBOARD_CARDS_2COL:
            cols = 2
        else:
            cols = 4
        if getattr(self, "_card_cols", None) == cols:
            return
        self._card_cols = cols
        self._position_cards(cols)

    def _rebuild_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        self._cards = []
        for title, value, color in self._card_data:
            card = ctk.CTkFrame(self.cards_frame, corner_radius=12)
            accent = ctk.CTkFrame(card, width=6, corner_radius=3, fg_color=color)
            accent.pack(side="left", fill="y", padx=(8, 0), pady=10)
            text_frame = ctk.CTkFrame(card, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=12, pady=12)
            ctk.CTkLabel(
                text_frame, text=title, font=ctk.CTkFont(size=12), text_color="gray"
            ).pack(anchor="w")
            ctk.CTkLabel(
                text_frame, text=value, font=ctk.CTkFont(size=22, weight="bold")
            ).pack(anchor="w")
            self._cards.append(card)
        self._card_cols = None
        self.cards_frame.after_idle(self._on_cards_resize)

    def _position_cards(self, cols):
        for i in range(cols):
            self.cards_frame.grid_columnconfigure(i, weight=1)
        for i, card in enumerate(self._cards):
            card.grid(
                row=i // cols,
                column=i % cols,
                padx=8,
                pady=8,
                sticky="nsew",
            )

    def layout_details(self, width):
        """Stack low-stock and maintenance panels vertically when narrow."""
        if width < DASHBOARD_CARDS_2COL:
            self.details_frame.grid_columnconfigure(0, weight=1)
            self.details_frame.grid_columnconfigure(1, weight=0)
            self.details_frame.grid_rowconfigure(0, weight=1)
            self.details_frame.grid_rowconfigure(1, weight=1)
            return "stack"
        self.details_frame.grid_columnconfigure(0, weight=1)
        self.details_frame.grid_columnconfigure(1, weight=1)
        self.details_frame.grid_rowconfigure(0, weight=1)
        return "split"


def center_toplevel(window):
    """Center a toplevel on the primary screen."""
    window.update_idletasks()
    w = window.winfo_width()
    h = window.winfo_height()
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x = max(0, (sw - w) // 2)
    y = max(0, (sh - h) // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")


class ResponsiveSideBySide:
    """Two panels placed side-by-side; stacks vertically when the container is narrow."""

    def __init__(self, parent, stack_at=SIDE_BY_SIDE_STACK_AT):
        self.stack_at = stack_at
        self._layout_mode = None
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        self.left = ctk.CTkFrame(self.container, fg_color="transparent")
        self.right = ctk.CTkFrame(self.container, fg_color="transparent")
        self.container.bind("<Configure>", self._on_resize, add="+")

    def _on_resize(self, _event=None):
        try:
            if not self.container.winfo_exists():
                return
            width = self.container.winfo_width()
            if width < 2:
                return
            if width < self.stack_at:
                self._apply_stack()
            else:
                self._apply_split()
        except tk.TclError:
            pass

    def _apply_split(self):
        if self._layout_mode == "split":
            return
        self._layout_mode = "split"
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=0)
        self.container.grid_rowconfigure(1, weight=0)
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        self.right.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

    def _apply_stack(self):
        if self._layout_mode == "stack":
            return
        self._layout_mode = "stack"
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)
        self.container.grid_rowconfigure(0, weight=0)
        self.container.grid_rowconfigure(1, weight=0)
        self.left.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 8))
        self.right.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

    def schedule_layout(self):
        self.container.after_idle(self._on_resize)
