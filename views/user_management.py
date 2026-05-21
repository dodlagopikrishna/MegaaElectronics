import customtkinter as ctk
from tkinter import messagebox
from login_manager import (
    get_all_users, get_all_roles, create_user, update_user,
    reset_user_password, delete_user, CurrentUser, is_default_admin,
)
from responsive_ui import (
    ResponsiveSplitView,
    render_table_header,
    render_table_row,
    grid_cell,
)


class UserManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.editing_id = None
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkLabel(self, text="User Management",
                              font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(anchor="w", padx=20, pady=(20, 10))

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkButton(
            top_bar,
            text="+ Add User",
            width=120,
            fg_color="#27ae60",
            hover_color="#219a52",
            command=self.show_add_form,
        ).pack(side="right")

        self.split = ResponsiveSplitView(self, table_weight=3, panel_weight=2)
        self.split.content.pack_configure(padx=20, pady=(0, 20))
        self.table_frame = self.split.table_inner
        self.form_frame = self.split.panel_frame

        self.refresh_table()
        self.show_empty_form()
        self.split.schedule_layout()

    def refresh_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        users = get_all_users()

        cols = ["Username", "Roles", "Status", "Actions"]
        weights = [2, 3, 1, 3]

        render_table_header(self.table_frame, cols, weights)

        role_colors = {"Admin": "#e74c3c", "Sales": "#27ae60",
                       "Inventory": "#2980b9", "Technician": "#8e44ad"}

        for user in users:
            row = render_table_row(self.table_frame, weights)

            username_text = user["username"]
            if user["is_default_admin"]:
                username_text += "  (default)"
            grid_cell(row, 0, username_text)

            roles_frame = ctk.CTkFrame(row, fg_color="transparent")
            roles_frame.grid(row=0, column=1, padx=8, pady=4, sticky="ew")
            for rname in user["role_names"]:
                color = role_colors.get(rname, "gray")
                ctk.CTkLabel(roles_frame, text=f" {rname} ", font=ctk.CTkFont(size=10),
                             corner_radius=4, fg_color=color,
                             text_color="white").pack(side="left", padx=1)

            status_text = "Active" if user["is_active"] else "Disabled"
            status_color = "#27ae60" if user["is_active"] else "#e74c3c"
            grid_cell(row, 2, status_text, text_color=status_color)

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.grid(row=0, column=3, padx=8, pady=4, sticky="ew")
            uid = user["id"]

            ctk.CTkButton(btn_frame, text="Edit", width=50, height=26,
                          font=ctk.CTkFont(size=11),
                          command=lambda u=uid: self.edit_user(u)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="Reset PW", width=70, height=26,
                          font=ctk.CTkFont(size=11), fg_color="#e67e22", hover_color="#d35400",
                          command=lambda u=uid: self.reset_password(u)).pack(side="left", padx=2)

            if uid != CurrentUser.get().user_id and not user["is_default_admin"]:
                ctk.CTkButton(btn_frame, text="Del", width=40, height=26,
                              font=ctk.CTkFont(size=11), fg_color="#e74c3c", hover_color="#c0392b",
                              command=lambda u=uid: self.del_user(u)).pack(side="left", padx=2)

        if not users:
            ctk.CTkLabel(self.table_frame, text="No users found.",
                         font=ctk.CTkFont(size=13), text_color="gray").pack(pady=30)

        self.split.table_frame._on_inner_configure()

    def show_empty_form(self):
        self.editing_id = None
        for w in self.form_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.form_frame, text="Select a user to edit\nor click '+ Add User'",
                     font=ctk.CTkFont(size=13), text_color="gray").pack(expand=True)

    def show_add_form(self):
        self.editing_id = None
        self._build_form()

    def _build_form(self, data=None):
        for w in self.form_frame.winfo_children():
            w.destroy()

        is_def_admin = data and data.get("is_default_admin", False)

        title = "Edit User" if data else "Add User"
        ctk.CTkLabel(self.form_frame, text=title,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(padx=15, pady=(15, 10))

        fields = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        fields.pack(fill="both", expand=True, padx=15, pady=5)

        ctk.CTkLabel(fields, text="Username").pack(anchor="w", pady=(5, 0))
        self.f_username = ctk.CTkEntry(fields)
        self.f_username.pack(fill="x", pady=(0, 5))

        if not data:
            ctk.CTkLabel(fields, text="Password").pack(anchor="w", pady=(5, 0))
            self.f_password = ctk.CTkEntry(fields, show="*")
            self.f_password.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields, text="Roles").pack(anchor="w", pady=(5, 0))

        if is_def_admin:
            ctk.CTkLabel(fields, text="Admin  (cannot be changed for default admin)",
                         font=ctk.CTkFont(size=11), text_color="#e67e22").pack(anchor="w", pady=(0, 5))
            self.role_checkboxes = {}
        else:
            roles = get_all_roles()
            existing_role_ids = set(data["role_ids"]) if data else set()
            self.role_checkboxes = {}

            roles_frame = ctk.CTkFrame(fields, fg_color="transparent")
            roles_frame.pack(fill="x", pady=(0, 5))

            for role in roles:
                var = ctk.IntVar(value=1 if role["id"] in existing_role_ids else 0)
                cb = ctk.CTkCheckBox(roles_frame, text=role["role_name"], variable=var,
                                     font=ctk.CTkFont(size=12))
                cb.pack(anchor="w", pady=2)
                self.role_checkboxes[role["id"]] = var

        if data:
            self.f_username.insert(0, data["username"])

            ctk.CTkLabel(fields, text="Status").pack(anchor="w", pady=(5, 0))
            self.f_active = ctk.CTkSwitch(fields, text="Active")
            if data["is_active"]:
                self.f_active.select()
            self.f_active.pack(anchor="w", pady=(0, 5))

        btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(btn_frame, text="Save", fg_color="#27ae60", hover_color="#219a52",
                      command=self.save_user).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray40",
                      command=self.show_empty_form).pack(side="left")

    def save_user(self):
        username = self.f_username.get().strip()
        if not username:
            messagebox.showwarning("Validation", "Username is required.")
            return

        editing_default_admin = self.editing_id and is_default_admin(self.editing_id)

        if editing_default_admin:
            selected_role_ids = None
        else:
            selected_role_ids = [rid for rid, var in self.role_checkboxes.items() if var.get()]
            if not selected_role_ids:
                messagebox.showwarning("Validation", "Select at least one role.")
                return

        if self.editing_id:
            is_active = int(self.f_active.get()) if hasattr(self, "f_active") else 1
            try:
                if editing_default_admin:
                    from database_setup import get_connection
                    conn = get_connection()
                    conn.execute(
                        "UPDATE users SET username = ?, is_active = ? WHERE id = ?",
                        (username, is_active, self.editing_id),
                    )
                    conn.commit()
                    conn.close()
                else:
                    update_user(self.editing_id, username, selected_role_ids, is_active)
            except Exception as e:
                messagebox.showerror("Error", f"Could not update user: {e}")
                return
        else:
            password = self.f_password.get().strip()
            if len(password) < 4:
                messagebox.showwarning("Validation", "Password must be at least 4 characters.")
                return
            try:
                create_user(username, password, selected_role_ids)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create user: {e}")
                return

        self.editing_id = None
        self.refresh_table()
        self.show_empty_form()

    def edit_user(self, user_id):
        users = get_all_users()
        data = None
        for u in users:
            if u["id"] == user_id:
                data = u
                break
        if data:
            self.editing_id = user_id
            self._build_form(data)

    def reset_password(self, user_id):
        dialog = ctk.CTkInputDialog(text="Enter new password:", title="Reset Password")
        new_pw = dialog.get_input()
        if new_pw and len(new_pw) >= 4:
            reset_user_password(user_id, new_pw)
            messagebox.showinfo("Done", "Password has been reset.")
        elif new_pw:
            messagebox.showwarning("Validation", "Password must be at least 4 characters.")

    def del_user(self, user_id):
        if is_default_admin(user_id):
            messagebox.showwarning("Protected", "The default admin account cannot be deleted.")
            return
        if messagebox.askyesno("Confirm", "Delete this user permanently?"):
            delete_user(user_id)
            self.refresh_table()
            self.show_empty_form()
