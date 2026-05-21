import customtkinter as ctk
from tkinter import messagebox
from models import get_all_products, add_product, update_product, delete_product
from models import get_all_services, add_service, update_service, delete_service
from login_manager import CurrentUser
from responsive_ui import (
    ResponsiveSplitView,
    build_toolbar,
    render_table_header,
    render_table_row,
    grid_cell,
    grid_actions,
)


class ProductsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.current_tab = "products"
        self.editing_id = None
        self.user = CurrentUser.get()
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkLabel(
            self,
            text="Product & Service Catalog",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.pack(anchor="w", padx=20, pady=(20, 10))

        tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_frame.pack(fill="x", padx=20)

        self.tab_products_btn = ctk.CTkButton(
            tab_frame,
            text="Products",
            command=lambda: self.switch_tab("products"),
            width=120,
            corner_radius=8,
        )
        self.tab_products_btn.pack(side="left", padx=(0, 5))

        self.tab_services_btn = ctk.CTkButton(
            tab_frame,
            text="Services",
            command=lambda: self.switch_tab("services"),
            width=120,
            corner_radius=8,
            fg_color="gray30",
        )
        self.tab_services_btn.pack(side="left", padx=5)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_table())

        can_edit = self.user.has_permission("Products_Edit") or self.user.has_permission(
            "Services_Edit"
        )
        build_toolbar(
            self,
            self.search_var,
            "Search...",
            add_text="+ Add New" if can_edit else None,
            add_command=self.show_add_form if can_edit else None,
            pady=(10, 5),
        )

        self.split = ResponsiveSplitView(self, table_weight=3, panel_weight=2)
        self.split.content.pack_configure(padx=20, pady=10)
        self.table_frame = self.split.table_inner
        self.form_frame = self.split.panel_frame

        self.refresh_table()
        self.show_empty_form()
        self.split.schedule_layout()

    def switch_tab(self, tab):
        self.current_tab = tab
        self.editing_id = None
        if tab == "products":
            self.tab_products_btn.configure(fg_color=("#3B8ED0", "#1F6AA5"))
            self.tab_services_btn.configure(fg_color="gray30")
        else:
            self.tab_services_btn.configure(fg_color=("#3B8ED0", "#1F6AA5"))
            self.tab_products_btn.configure(fg_color="gray30")
        self.refresh_table()
        self.show_empty_form()

    def refresh_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        search = self.search_var.get()

        if self.current_tab == "products":
            items = get_all_products(search)
            self._render_product_table(items)
        else:
            items = get_all_services(search)
            self._render_service_table(items)

        self.split.table_frame._on_inner_configure()

    def _render_product_table(self, items):
        show_cost = self.user.has_permission("Cost_Prices")
        can_edit = self.user.has_permission("Products_Edit")
        can_delete = self.user.has_permission("Products_Delete")
        show_actions = can_edit or can_delete

        cols = ["Name", "Category"]
        weights = [3, 2]
        if show_cost:
            cols.append("Cost")
            weights.append(1)
        cols.extend(["Retail", "Stock", "Unit"])
        weights.extend([1, 1, 1])
        if show_actions:
            cols.append("Actions")
            weights.append(2)

        render_table_header(self.table_frame, cols, weights)

        for item in items:
            row = render_table_row(self.table_frame, weights)
            col_idx = 0
            grid_cell(row, col_idx, item["name"])
            col_idx += 1
            grid_cell(row, col_idx, item["category"])
            col_idx += 1

            if show_cost:
                grid_cell(row, col_idx, f"₹{item['cost_price']:.2f}")
                col_idx += 1

            grid_cell(row, col_idx, f"₹{item['retail_price']:.2f}")
            col_idx += 1

            stock_color = "#e74c3c" if item["stock_count"] <= 5 else None
            grid_cell(row, col_idx, str(item["stock_count"]), text_color=stock_color)
            col_idx += 1

            grid_cell(row, col_idx, item["unit"])
            col_idx += 1

            if show_actions:
                pid = item["id"]
                buttons = []
                if can_edit:
                    buttons.append(("Edit", lambda p=pid: self.edit_product(p), {}))
                if can_delete:
                    buttons.append(
                        (
                            "Del",
                            lambda p=pid: self.del_product(p),
                            {"fg_color": "#e74c3c", "hover_color": "#c0392b"},
                        )
                    )
                grid_actions(row, col_idx, buttons)

        if not items:
            ctk.CTkLabel(
                self.table_frame,
                text="No products found.",
                font=ctk.CTkFont(size=13),
                text_color="gray",
            ).pack(pady=30)

    def _render_service_table(self, items):
        can_edit = self.user.has_permission("Services_Edit")
        can_delete = self.user.has_permission("Services_Delete")
        show_actions = can_edit or can_delete

        cols = ["Name", "Type", "Rate", "Rate Type"]
        weights = [3, 2, 1, 2]
        if show_actions:
            cols.append("Actions")
            weights.append(2)

        render_table_header(self.table_frame, cols, weights, header_color="#8e44ad")

        for item in items:
            row = render_table_row(self.table_frame, weights)
            grid_cell(row, 0, item["name"])
            grid_cell(row, 1, item["service_type"])
            grid_cell(row, 2, f"₹{item['rate']:.2f}")
            grid_cell(row, 3, item["rate_type"])

            if show_actions:
                sid = item["id"]
                buttons = []
                if can_edit:
                    buttons.append(("Edit", lambda s=sid: self.edit_service(s), {}))
                if can_delete:
                    buttons.append(
                        (
                            "Del",
                            lambda s=sid: self.del_service(s),
                            {"fg_color": "#e74c3c", "hover_color": "#c0392b"},
                        )
                    )
                grid_actions(row, 4, buttons)

        if not items:
            ctk.CTkLabel(
                self.table_frame,
                text="No services found.",
                font=ctk.CTkFont(size=13),
                text_color="gray",
            ).pack(pady=30)

    # ── Form Logic ────────────────────────────────────────────

    def show_empty_form(self):
        self.editing_id = None
        for w in self.form_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.form_frame,
            text="Select an item to edit\nor click '+ Add New'",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).pack(expand=True)

    def show_add_form(self):
        self.editing_id = None
        if self.current_tab == "products":
            self._build_product_form()
        else:
            self._build_service_form()

    def _build_product_form(self, data=None):
        for w in self.form_frame.winfo_children():
            w.destroy()

        show_cost = self.user.has_permission("Cost_Prices")

        title = "Edit Product" if data else "Add Product"
        ctk.CTkLabel(
            self.form_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=15, pady=(15, 10))

        fields_frame = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=15, pady=5)

        ctk.CTkLabel(fields_frame, text="Name").pack(anchor="w", pady=(5, 0))
        self.f_name = ctk.CTkEntry(fields_frame)
        self.f_name.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields_frame, text="Category").pack(anchor="w", pady=(5, 0))
        self.f_category = ctk.CTkComboBox(
            fields_frame, values=["CCTV", "Projector", "Accessories", "Other"]
        )
        self.f_category.pack(fill="x", pady=(0, 5))

        if show_cost:
            ctk.CTkLabel(fields_frame, text="Cost Price (₹)").pack(anchor="w", pady=(5, 0))
            self.f_cost = ctk.CTkEntry(fields_frame)
            self.f_cost.pack(fill="x", pady=(0, 5))
        else:
            self.f_cost = None

        ctk.CTkLabel(fields_frame, text="Retail Price (₹)").pack(anchor="w", pady=(5, 0))
        self.f_retail = ctk.CTkEntry(fields_frame)
        self.f_retail.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields_frame, text="Stock Quantity").pack(anchor="w", pady=(5, 0))
        self.f_stock = ctk.CTkEntry(fields_frame)
        self.f_stock.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields_frame, text="Unit").pack(anchor="w", pady=(5, 0))
        self.f_unit = ctk.CTkComboBox(
            fields_frame, values=["pcs", "meters", "sets", "rolls"]
        )
        self.f_unit.pack(fill="x", pady=(0, 5))

        if data:
            self.f_name.insert(0, data["name"])
            self.f_category.set(data["category"])
            if self.f_cost:
                self.f_cost.insert(0, str(data["cost_price"]))
            self.f_retail.insert(0, str(data["retail_price"]))
            self.f_stock.insert(0, str(data["stock_count"]))
            self.f_unit.set(data["unit"])

        btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(
            btn_frame,
            text="Save",
            fg_color="#27ae60",
            hover_color="#219a52",
            command=self.save_product,
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="gray40", command=self.show_empty_form
        ).pack(side="left")

    def _build_service_form(self, data=None):
        for w in self.form_frame.winfo_children():
            w.destroy()

        title = "Edit Service" if data else "Add Service"
        ctk.CTkLabel(
            self.form_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=15, pady=(15, 10))

        fields_frame = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=15, pady=5)

        ctk.CTkLabel(fields_frame, text="Name").pack(anchor="w", pady=(5, 0))
        self.f_name = ctk.CTkEntry(fields_frame)
        self.f_name.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields_frame, text="Description").pack(anchor="w", pady=(5, 0))
        self.f_desc = ctk.CTkEntry(fields_frame)
        self.f_desc.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields_frame, text="Rate (₹)").pack(anchor="w", pady=(5, 0))
        self.f_rate = ctk.CTkEntry(fields_frame)
        self.f_rate.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields_frame, text="Rate Type").pack(anchor="w", pady=(5, 0))
        self.f_rate_type = ctk.CTkComboBox(
            fields_frame, values=["Flat Fee", "Hourly Rate"]
        )
        self.f_rate_type.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(fields_frame, text="Service Type").pack(anchor="w", pady=(5, 0))
        self.f_svc_type = ctk.CTkComboBox(
            fields_frame, values=["Installation", "Maintenance"]
        )
        self.f_svc_type.pack(fill="x", pady=(0, 5))

        if data:
            self.f_name.insert(0, data["name"])
            self.f_desc.insert(0, data.get("description", ""))
            self.f_rate.insert(0, str(data["rate"]))
            self.f_rate_type.set(data["rate_type"])
            self.f_svc_type.set(data["service_type"])

        btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(
            btn_frame,
            text="Save",
            fg_color="#27ae60",
            hover_color="#219a52",
            command=self.save_service,
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="gray40", command=self.show_empty_form
        ).pack(side="left")

    # ── CRUD Operations ───────────────────────────────────────

    def save_product(self):
        try:
            name = self.f_name.get().strip()
            if not name:
                messagebox.showwarning("Validation", "Product name is required.")
                return
            category = self.f_category.get()
            cost = float(self.f_cost.get() or 0) if self.f_cost else 0
            retail = float(self.f_retail.get() or 0)
            stock = int(self.f_stock.get() or 0)
            unit = self.f_unit.get()

            if self.editing_id:
                existing = __import__("models").get_product(self.editing_id)
                if not self.f_cost and existing:
                    cost = existing["cost_price"]
                update_product(self.editing_id, name, category, cost, retail, stock, unit)
            else:
                add_product(name, category, cost, retail, stock, unit)

            self.editing_id = None
            self.refresh_table()
            self.show_empty_form()
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numeric values for prices and stock."
            )

    def save_service(self):
        try:
            name = self.f_name.get().strip()
            if not name:
                messagebox.showwarning("Validation", "Service name is required.")
                return
            desc = self.f_desc.get().strip()
            rate = float(self.f_rate.get() or 0)
            rate_type = self.f_rate_type.get()
            svc_type = self.f_svc_type.get()

            if self.editing_id:
                update_service(self.editing_id, name, desc, rate, rate_type, svc_type)
            else:
                add_service(name, desc, rate, rate_type, svc_type)

            self.editing_id = None
            self.refresh_table()
            self.show_empty_form()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric rate.")

    def edit_product(self, product_id):
        from models import get_product

        data = get_product(product_id)
        if data:
            self.editing_id = product_id
            self._build_product_form(data)

    def edit_service(self, service_id):
        from models import get_service

        data = get_service(service_id)
        if data:
            self.editing_id = service_id
            self._build_service_form(data)

    def del_product(self, product_id):
        if messagebox.askyesno("Confirm", "Delete this product?"):
            delete_product(product_id)
            self.refresh_table()
            self.show_empty_form()

    def del_service(self, service_id):
        if messagebox.askyesno("Confirm", "Delete this service?"):
            delete_service(service_id)
            self.refresh_table()
            self.show_empty_form()
