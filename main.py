import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_setup import initialize_database, seed_sample_data, DB_PATH
from login_manager import bootstrap_admin, CurrentUser
from views.login import LoginWindow
from views.dashboard import DashboardView
from views.products import ProductsView
from views.clients import ClientsView
from views.quotes import QuotesView
from views.invoices import InvoicesView
from views.user_management import UserManagementView
from views.change_password import ChangePasswordView
from responsive_ui import (
    SIDEBAR_COLLAPSE_WIDTH,
    SIDEBAR_WIDTH_FULL,
    SIDEBAR_WIDTH_COMPACT,
    apply_scroll_theme,
)


NAV_PERMISSIONS = {
    "dashboard":  "Dashboard",
    "products":   "Products_View",
    "clients":    "Clients_View",
    "quotes":     "Quotes_View",
    "invoices":   "Invoices_View",
    "users":      "User_Management",
}

NAV_LABELS = {
    "dashboard": "Dashboard",
    "products":  "Inventory",
    "clients":   "Clients",
    "quotes":    "Quotes",
    "invoices":  "Invoices",
    "users":     "User Mgmt",
}

VIEW_CLASSES = {
    "dashboard": DashboardView,
    "products":  ProductsView,
    "clients":   ClientsView,
    "quotes":    QuotesView,
    "invoices":  InvoicesView,
    "users":     UserManagementView,
    "change_password": ChangePasswordView,
}


class MEGAApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MEGA Electronics - Retail Management")
        self.geometry("1280x780")
        self.minsize(800, 500)
        self._sidebar_compact = False

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        initialize_database()
        seed_sample_data()
        bootstrap_admin()

        self.withdraw()
        self.after(100, self._show_login)

    def _show_login(self):
        LoginWindow(self, on_success=self._on_login_success)

    def _on_login_success(self):
        self.deiconify()
        self._build_layout()

        allowed = self._get_allowed_views()
        first_view = allowed[0] if allowed else "dashboard"
        self.show_view(first_view)

    def _get_allowed_views(self):
        current = CurrentUser.get()
        ordered_keys = ["dashboard", "products", "clients", "quotes", "invoices", "users"]
        return [k for k in ordered_keys if current.has_permission(NAV_PERMISSIONS[k])]

    def _build_layout(self):
        for w in self.winfo_children():
            w.destroy()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        current = CurrentUser.get()
        allowed = self._get_allowed_views()

        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH_FULL, corner_radius=0, fg_color="#1a1a2e")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self._nav_labels_full = {}

        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.pack(fill="x", padx=15, pady=(20, 5))
        brand_frame = self.brand_frame

        ctk.CTkLabel(brand_frame, text="MEGA",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color="#2980b9").pack(anchor="w")
        ctk.CTkLabel(brand_frame, text="Electronics",
                     font=ctk.CTkFont(size=14),
                     text_color="#7f8c8d").pack(anchor="w")

        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#16213e", corner_radius=8)
        user_frame.pack(fill="x", padx=15, pady=(10, 0))
        ctk.CTkLabel(user_frame, text=f"{current.username}",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(8, 0))
        roles_text = ", ".join(current.role_names) if current.role_names else "No roles"
        ctk.CTkLabel(user_frame, text=roles_text,
                     font=ctk.CTkFont(size=11), text_color="#2980b9").pack(anchor="w", padx=10, pady=(0, 8))

        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="#2c3e50")
        separator.pack(fill="x", padx=15, pady=15)

        self.nav_buttons = {}
        for key in allowed:
            label = NAV_LABELS[key]
            self._nav_labels_full[key] = label
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {label}",
                anchor="w",
                height=42,
                corner_radius=8,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color="#bdc3c7",
                hover_color="#2c3e50",
                command=lambda k=key: self.show_view(k),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn

        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        self.change_pw_btn = ctk.CTkButton(
            self.sidebar, text="Change Password", height=32,
            font=ctk.CTkFont(size=11), fg_color="#2c3e50", hover_color="#34495e",
            command=self._show_change_password,
        )
        self.change_pw_btn.pack(fill="x", padx=10, pady=(0, 5))

        self.theme_btn = ctk.CTkButton(
            self.sidebar, text="Toggle Light/Dark", height=32,
            font=ctk.CTkFont(size=11), fg_color="#2c3e50", hover_color="#34495e",
            command=self._toggle_theme,
        )
        self.theme_btn.pack(fill="x", padx=10, pady=(0, 5))

        logout_btn = ctk.CTkButton(
            self.sidebar, text="Logout", height=32,
            font=ctk.CTkFont(size=11), fg_color="#c0392b", hover_color="#e74c3c",
            command=self._logout,
        )
        logout_btn.pack(fill="x", padx=10, pady=(0, 5))

        version_label = ctk.CTkLabel(self.sidebar, text="v2.0.0",
                                     font=ctk.CTkFont(size=10), text_color="#555")
        version_label.pack(pady=(0, 15))

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")

        self.current_view = None
        self._active_view = None
        self.bind("<Configure>", self._on_window_resize, add="+")
        self.after_idle(self._on_window_resize)

    def show_view(self, view_name):
        self._active_view = view_name
        for key, btn in self.nav_buttons.items():
            if key == view_name:
                btn.configure(fg_color="#2980b9", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#bdc3c7")

        if hasattr(self, "change_pw_btn"):
            if view_name == "change_password":
                self.change_pw_btn.configure(fg_color="#2980b9", text_color="white")
            else:
                self.change_pw_btn.configure(
                    fg_color="#2c3e50", text_color=("gray10", "gray90")
                )

        if self.current_view:
            self.current_view.destroy()

        view_class = VIEW_CLASSES.get(view_name, DashboardView)
        self.current_view = view_class(self.main_area)
        self.current_view.pack(fill="both", expand=True)

    def _on_window_resize(self, _event=None):
        if not hasattr(self, "sidebar") or not self.sidebar.winfo_exists():
            return
        compact = self.winfo_width() < SIDEBAR_COLLAPSE_WIDTH
        if compact == self._sidebar_compact:
            return
        self._sidebar_compact = compact
        width = SIDEBAR_WIDTH_COMPACT if compact else SIDEBAR_WIDTH_FULL
        self.sidebar.configure(width=width)
        for key, btn in self.nav_buttons.items():
            full = self._nav_labels_full.get(key, NAV_LABELS.get(key, key))
            short = full[:4] if compact else full
            btn.configure(text=f"  {short}", anchor="center" if compact else "w")
        if hasattr(self, "change_pw_btn"):
            self.change_pw_btn.configure(text="Password" if compact else "Change Password")
        if hasattr(self, "theme_btn"):
            self.theme_btn.configure(text="Theme" if compact else "Toggle Light/Dark")

    def _show_change_password(self):
        self.show_view("change_password")

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        if self.current_view:
            apply_scroll_theme(self.current_view)

    def _logout(self):
        CurrentUser.get().logout()
        for w in self.winfo_children():
            w.destroy()
        self.current_view = None
        self.withdraw()
        self.after(100, self._show_login)


if __name__ == "__main__":
    app = MEGAApp()
    app.mainloop()
