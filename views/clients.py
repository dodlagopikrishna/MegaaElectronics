import customtkinter as ctk
from tkinter import messagebox
from models import get_all_clients, add_client, update_client, delete_client, get_client
from login_manager import CurrentUser
from responsive_ui import (
    ResponsiveSplitView,
    build_toolbar,
    render_table_header,
    render_table_row,
    grid_cell,
    grid_actions,
)


class ClientsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.editing_id = None
        self.user = CurrentUser.get()
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkLabel(
            self, text="Client Management", font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(anchor="w", padx=20, pady=(20, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_table())

        if self.user.has_permission("Clients_Edit"):
            build_toolbar(
                self,
                self.search_var,
                "Search clients...",
                add_text="+ Add Client",
                add_command=self.show_add_form,
            )
        else:
            build_toolbar(self, self.search_var, "Search clients...")

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

        clients = get_all_clients(self.search_var.get())

        can_edit = self.user.has_permission("Clients_Edit")
        can_delete = self.user.has_permission("Clients_Delete")
        show_actions = can_edit or can_delete

        cols = ["Name", "Phone", "Email"]
        weights = [3, 2, 3]
        if show_actions:
            cols.append("Actions")
            weights.append(2)

        render_table_header(self.table_frame, cols, weights)

        for client in clients:
            row = render_table_row(self.table_frame, weights)
            grid_cell(row, 0, client["name"])
            grid_cell(row, 1, client["phone"])
            grid_cell(row, 2, client["email"])

            if show_actions:
                cid = client["id"]
                buttons = []
                if can_edit:
                    buttons.append(("Edit", lambda c=cid: self.edit_client(c), {}))
                if can_delete:
                    buttons.append(
                        (
                            "Del",
                            lambda c=cid: self.del_client(c),
                            {"fg_color": "#e74c3c", "hover_color": "#c0392b"},
                        )
                    )
                grid_actions(row, 3, buttons)

        if not clients:
            ctk.CTkLabel(
                self.table_frame,
                text="No clients found.",
                font=ctk.CTkFont(size=13),
                text_color="gray",
            ).pack(pady=30)

        self.split.table_frame._on_inner_configure()

    def show_empty_form(self):
        self.editing_id = None
        for w in self.form_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.form_frame,
            text="Select a client to edit\nor click '+ Add Client'",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).pack(expand=True)

    def show_add_form(self):
        self.editing_id = None
        self._build_form()

    def _build_form(self, data=None):
        for w in self.form_frame.winfo_children():
            w.destroy()

        title = "Edit Client" if data else "Add Client"
        ctk.CTkLabel(
            self.form_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=15, pady=(15, 10))

        fields = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        fields.pack(fill="both", expand=True, padx=15, pady=5)

        ctk.CTkLabel(fields, text="Name").pack(anchor="w", pady=(5, 0))
        self.f_name = ctk.CTkEntry(fields)
        self.f_name.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields, text="Phone").pack(anchor="w", pady=(5, 0))
        self.f_phone = ctk.CTkEntry(fields)
        self.f_phone.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields, text="Email").pack(anchor="w", pady=(5, 0))
        self.f_email = ctk.CTkEntry(fields)
        self.f_email.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields, text="Address").pack(anchor="w", pady=(5, 0))
        self.f_address = ctk.CTkTextbox(fields, height=80)
        self.f_address.pack(fill="x", pady=(0, 5))

        if data:
            self.f_name.insert(0, data["name"])
            self.f_phone.insert(0, data.get("phone", ""))
            self.f_email.insert(0, data.get("email", ""))
            self.f_address.insert("1.0", data.get("address", ""))

        btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(
            btn_frame,
            text="Save",
            fg_color="#27ae60",
            hover_color="#219a52",
            command=self.save_client,
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="gray40", command=self.show_empty_form
        ).pack(side="left")

    def save_client(self):
        name = self.f_name.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Client name is required.")
            return
        phone = self.f_phone.get().strip()
        email = self.f_email.get().strip()
        address = self.f_address.get("1.0", "end-1c").strip()

        if self.editing_id:
            update_client(self.editing_id, name, phone, email, address)
        else:
            add_client(name, phone, email, address)

        self.editing_id = None
        self.refresh_table()
        self.show_empty_form()

    def edit_client(self, client_id):
        data = get_client(client_id)
        if data:
            self.editing_id = client_id
            self._build_form(data)

    def del_client(self, client_id):
        if messagebox.askyesno("Confirm", "Delete this client?"):
            delete_client(client_id)
            self.refresh_table()
            self.show_empty_form()
