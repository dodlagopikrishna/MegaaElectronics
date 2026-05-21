import customtkinter as ctk
from login_manager import authenticate, CurrentUser
from responsive_ui import (
    LOGIN_MIN_WIDTH,
    LOGIN_MIN_HEIGHT,
    LOGIN_DEFAULT_WIDTH,
    LOGIN_DEFAULT_HEIGHT,
    LOGIN_PADDING_NARROW,
    LOGIN_PADDING_WIDE,
    LOGIN_NARROW_WIDTH,
    center_toplevel,
)

LOGIN_FORM_MAX_WIDTH = 400
LOGIN_FORM_MIN_WIDTH = 280


class LoginWindow(ctk.CTkToplevel):
    """Modal login window that blocks access to the main application."""

    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.result = False

        self.title("MEGA Electronics - Login")
        self.geometry(f"{LOGIN_DEFAULT_WIDTH}x{LOGIN_DEFAULT_HEIGHT}")
        self.minsize(LOGIN_MIN_WIDTH, LOGIN_MIN_HEIGHT)
        self.resizable(True, True)
        self.grab_set()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.configure(fg_color="#1a1a2e")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self._build_ui()
        self.bind("<Configure>", self._on_resize, add="+")
        self.after_idle(self._apply_layout)
        self.after(50, center_toplevel)

    def _build_ui(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)

        self.brand_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.brand_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.brand_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.brand_frame,
            text="MEGA",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#2980b9",
            anchor="center",
        ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            self.brand_frame,
            text="Electronics",
            font=ctk.CTkFont(size=16),
            text_color="#7f8c8d",
            anchor="center",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.subtitle_label = ctk.CTkLabel(
            self.brand_frame,
            text="Retail Management System",
            font=ctk.CTkFont(size=11),
            text_color="#555",
            anchor="center",
            justify="center",
        )
        self.subtitle_label.grid(row=2, column=0, sticky="ew", pady=(0, 16))

        self.form = ctk.CTkFrame(self.content, fg_color="#16213e", corner_radius=16)
        self.form.grid(row=1, column=0, sticky="ew")
        self.form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.form,
            text="Sign In",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=25, pady=(25, 15), sticky="ew")

        ctk.CTkLabel(
            self.form,
            text="Username",
            font=ctk.CTkFont(size=12),
            text_color="#bdc3c7",
        ).grid(row=1, column=0, padx=25, sticky="w")
        self.username_entry = ctk.CTkEntry(
            self.form, placeholder_text="Enter username", height=36
        )
        self.username_entry.grid(row=2, column=0, padx=25, pady=(2, 10), sticky="ew")

        ctk.CTkLabel(
            self.form,
            text="Password",
            font=ctk.CTkFont(size=12),
            text_color="#bdc3c7",
        ).grid(row=3, column=0, padx=25, sticky="w")
        self.password_entry = ctk.CTkEntry(
            self.form, placeholder_text="Enter password", show="*", height=36
        )
        self.password_entry.grid(row=4, column=0, padx=25, pady=(2, 15), sticky="ew")

        self.login_btn = ctk.CTkButton(
            self.form,
            text="Login",
            height=38,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2980b9",
            hover_color="#1F6AA5",
            command=self._do_login,
        )
        self.login_btn.grid(row=5, column=0, padx=25, pady=(0, 5), sticky="ew")

        self.status_label = ctk.CTkLabel(
            self.form,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#e74c3c",
            anchor="center",
        )
        self.status_label.grid(row=6, column=0, padx=25, pady=(0, 20), sticky="ew")

        self.password_entry.bind("<Return>", lambda e: self._do_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        self.after(100, lambda: self.username_entry.focus())

    def _on_resize(self, event=None):
        if event is not None and event.widget is not self:
            return
        self._apply_layout()

    def _apply_layout(self):
        try:
            if not self.winfo_exists():
                return
            width = self.winfo_width()
            if width < 2:
                return

            pad = LOGIN_PADDING_NARROW if width < LOGIN_NARROW_WIDTH else LOGIN_PADDING_WIDE
            content_w = min(
                LOGIN_FORM_MAX_WIDTH,
                max(LOGIN_FORM_MIN_WIDTH, width - pad * 2),
            )
            self.grid_columnconfigure(1, minsize=content_w)
            self.content.grid_configure(padx=pad)
            self.subtitle_label.configure(wraplength=max(160, content_w - 40))
        except Exception:
            pass

    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.status_label.configure(text="Please enter both fields")
            return

        self.login_btn.configure(state="disabled", text="Verifying...")

        user, permissions = authenticate(username, password)

        if user is None:
            self.status_label.configure(text="Invalid username or password")
            self.login_btn.configure(state="normal", text="Login")
            return

        current = CurrentUser.get()
        current.login(user, permissions)

        self.result = True
        self.grab_release()
        self.destroy()
        self.on_success()

    def _on_close(self):
        CurrentUser.get().logout()
        self.result = False
        self.grab_release()
        self.destroy()
        try:
            self.master.destroy()
        except Exception:
            pass
