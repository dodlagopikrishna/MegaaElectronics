import customtkinter as ctk
from tkinter import messagebox
from login_manager import CurrentUser, change_own_password
from responsive_ui import ResponsiveSplitView


class ChangePasswordView(ctk.CTkFrame):
    """Change password for the logged-in user in the main content area."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkLabel(
            self,
            text="Change Password",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.pack(anchor="w", padx=20, pady=(20, 10))

        self.split = ResponsiveSplitView(
            self, table_weight=2, panel_weight=3, stack_at=700
        )
        self.split.content.pack_configure(padx=20, pady=(0, 20))
        self.info_frame = self.split.table_inner
        self.form_frame = self.split.panel_frame

        self._build_info_panel()
        self._build_form_panel()
        self.split.schedule_layout()

    def _build_info_panel(self):
        current = CurrentUser.get()

        card = ctk.CTkFrame(self.info_frame, corner_radius=12)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            card,
            text="Your Account",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 15))

        for label, value in [
            ("Username", current.username),
            ("Roles", ", ".join(current.role_names) if current.role_names else "None"),
        ]:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(
                row, text=label, font=ctk.CTkFont(size=12), text_color="gray", width=80
            ).pack(side="left", anchor="w")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=13, weight="bold")).pack(
                side="left", anchor="w"
            )

    def _build_form_panel(self):
        panel = ctk.CTkFrame(self.form_frame, corner_radius=12)
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            panel,
            text="New Password",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 10))

        fields = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        fields.pack(fill="both", expand=True, padx=20, pady=5)

        ctk.CTkLabel(fields, text="New Password").pack(anchor="w", pady=(5, 0))
        self.new_pw_entry = ctk.CTkEntry(fields, show="*", height=36)
        self.new_pw_entry.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(fields, text="Confirm New Password").pack(anchor="w", pady=(5, 0))
        self.confirm_pw_entry = ctk.CTkEntry(fields, show="*", height=36)
        self.confirm_pw_entry.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(
            fields,
            text="Minimum 4 characters.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).pack(anchor="w", pady=(0, 5))

        self.status_label = ctk.CTkLabel(
            fields, text="", font=ctk.CTkFont(size=11), text_color="#e74c3c"
        )
        self.status_label.pack(anchor="w", pady=(5, 0))

        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Save Password",
            fg_color="#27ae60",
            hover_color="#219a52",
            command=self._save,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btn_frame,
            text="Clear",
            fg_color="gray40",
            command=self._clear_form,
        ).pack(side="left")

        self.new_pw_entry.bind("<Return>", lambda e: self.confirm_pw_entry.focus())
        self.confirm_pw_entry.bind("<Return>", lambda e: self._save())

    def _clear_form(self):
        self.new_pw_entry.delete(0, "end")
        self.confirm_pw_entry.delete(0, "end")
        self.status_label.configure(text="")

    def _save(self):
        new_pw = self.new_pw_entry.get().strip()
        confirm_pw = self.confirm_pw_entry.get().strip()

        if not new_pw:
            self.status_label.configure(text="Enter a new password.")
            return
        if new_pw != confirm_pw:
            self.status_label.configure(text="New passwords do not match.")
            return

        ok, message = change_own_password(new_pw)
        if ok:
            messagebox.showinfo("Done", "Your password has been changed.")
            self._clear_form()
            return

        self.status_label.configure(text=message)
