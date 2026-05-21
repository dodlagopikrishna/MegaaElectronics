import customtkinter as ctk
from tkinter import messagebox
import subprocess, sys, os
from models import (
    get_all_clients, get_all_products, get_all_services,
    get_all_transactions, get_transaction, get_transaction_items,
    create_transaction, update_transaction_status, delete_transaction,
    decrement_stock,
)
from pdf_generator import generate_transaction_pdf
from login_manager import CurrentUser
from responsive_ui import ResponsiveSplitView, ResponsiveSideBySide, build_toolbar


class InvoicesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.line_items = []
        self.user = CurrentUser.get()
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkLabel(self, text="Invoices",
                              font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(anchor="w", padx=20, pady=(20, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())

        build_toolbar(
            self,
            self.search_var,
            "Search invoices...",
            add_text="+ Direct Invoice" if self.user.has_permission("Invoices_Create") else None,
            add_command=self.show_builder if self.user.has_permission("Invoices_Create") else None,
            pady=(0, 5),
        )

        self.split = ResponsiveSplitView(
            self, table_weight=2, panel_weight=3, use_dual_scroll=False
        )
        self.split.content.pack_configure(padx=20, pady=(0, 20))
        self.list_frame = self.split.table_frame
        self.detail_frame = self.split.panel_frame

        self.refresh_list()
        self._show_empty_detail()
        self.split.schedule_layout()

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        invoices = get_all_transactions(self.search_var.get(), tx_type="Invoice")
        can_delete = self.user.has_permission("Invoices_Delete")
        can_export = self.user.has_permission("Export_PDF")

        if not invoices:
            ctk.CTkLabel(self.list_frame, text="No invoices yet.",
                         font=ctk.CTkFont(size=13), text_color="gray").pack(pady=30)
            return

        for inv in invoices:
            card = ctk.CTkFrame(self.list_frame, corner_radius=8)
            card.pack(fill="x", pady=3)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(info, text=f"INV-{inv['id']:04d}",
                         font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"{inv.get('client_name', 'Walk-in')}  |  {inv['date']}",
                         font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")

            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=10, pady=(0, 8))
            bottom.grid_columnconfigure(0, weight=1)

            status_color = "#27ae60" if inv["status"] == "Paid" else "#e67e22"
            ctk.CTkLabel(
                bottom,
                text=f"₹{inv['total_amount']:,.2f}  [{inv['status']}]",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=status_color,
            ).grid(row=0, column=0, sticky="w")

            iid = inv["id"]
            btn_row = ctk.CTkFrame(bottom, fg_color="transparent")
            btn_row.grid(row=0, column=1, sticky="e")

            ctk.CTkButton(btn_row, text="View", width=50, height=24,
                          font=ctk.CTkFont(size=11),
                          command=lambda e=iid: self.view_invoice(e)).pack(side="left", padx=2)
            if can_export:
                ctk.CTkButton(btn_row, text="PDF", width=50, height=24,
                              font=ctk.CTkFont(size=11), fg_color="#8e44ad",
                              command=lambda e=iid: self.export_pdf(e)).pack(side="left", padx=2)

            if inv["status"] == "Pending":
                ctk.CTkButton(btn_row, text="Paid", width=50, height=24,
                              font=ctk.CTkFont(size=11), fg_color="#27ae60",
                              command=lambda e=iid: self.mark_paid(e)).pack(side="left", padx=2)

            if can_delete:
                ctk.CTkButton(btn_row, text="Del", width=40, height=24,
                              font=ctk.CTkFont(size=11), fg_color="#e74c3c", hover_color="#c0392b",
                              command=lambda e=iid: self.del_invoice(e)).pack(side="left", padx=2)

    def _show_empty_detail(self):
        for w in self.detail_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.detail_frame, text="Select an invoice or create a new one",
                     font=ctk.CTkFont(size=13), text_color="gray").pack(expand=True)

    # ── Direct Invoice Builder ────────────────────────────────

    def show_builder(self):
        self.line_items = []
        for w in self.detail_frame.winfo_children():
            w.destroy()

        builder = ctk.CTkScrollableFrame(self.detail_frame, fg_color="transparent")
        builder.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(builder, text="New Direct Invoice",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        client_frame = ctk.CTkFrame(builder, fg_color="transparent")
        client_frame.pack(fill="x", padx=10, pady=5)
        client_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(client_frame, text="Client:").grid(row=0, column=0, sticky="w")

        clients = get_all_clients()
        client_names = ["-- Walk-in --"] + [f"{c['id']}: {c['name']}" for c in clients]
        self.client_combo = ctk.CTkComboBox(client_frame, values=client_names)
        self.client_combo.grid(row=0, column=1, padx=10, sticky="ew")

        add_frame = ctk.CTkFrame(builder, corner_radius=8)
        add_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(add_frame, text="Add Item",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=10, pady=(8, 2))

        search_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        search_row.pack(fill="x", padx=10, pady=5)
        search_row.grid_columnconfigure(0, weight=1)

        self.item_search_var = ctk.StringVar()
        self._search_after_id = None
        self.item_search_var.trace_add("write", lambda *_: self._debounced_search())
        ctk.CTkEntry(
            search_row,
            placeholder_text="Type to search products & services...",
            textvariable=self.item_search_var,
        ).grid(row=0, column=0, sticky="ew")

        self.item_results_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        self.item_results_frame.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(builder, text="Line Items",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 2))

        self.items_display = ctk.CTkFrame(builder, corner_radius=8)
        self.items_display.pack(fill="x", padx=10, pady=5)
        self._refresh_line_items()

        calc = ResponsiveSideBySide(builder)
        calc.container.pack(fill="x", padx=10, pady=5)
        left_calc = calc.left
        right_calc = calc.right

        ctk.CTkLabel(left_calc, text="Tax Rate (%)").pack(anchor="w")
        self.tax_var = ctk.CTkEntry(left_calc, width=100)
        self.tax_var.insert(0, "9")
        self.tax_var.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(left_calc, text="Discount (%)").pack(anchor="w")
        self.discount_var = ctk.CTkEntry(left_calc, width=100)
        self.discount_var.insert(0, "0")
        self.discount_var.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(right_calc, text="Notes").pack(anchor="w")
        self.notes_var = ctk.CTkTextbox(right_calc, height=60)
        self.notes_var.pack(fill="x", pady=(0, 5))
        calc.schedule_layout()

        self.totals_label = ctk.CTkLabel(builder, text="",
                                         font=ctk.CTkFont(size=13), justify="right")
        self.totals_label.pack(anchor="e", padx=10, pady=5)
        self._update_totals()

        btn_frame = ctk.CTkFrame(builder, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(5, 15))

        ctk.CTkButton(btn_frame, text="Save Invoice", fg_color="#27ae60",
                      hover_color="#219a52", command=self.save_invoice).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray40",
                      command=self._show_empty_detail).pack(side="left")

    def _debounced_search(self):
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(250, self.search_items)

    def search_items(self):
        self._search_after_id = None
        for w in self.item_results_frame.winfo_children():
            w.destroy()

        query = self.item_search_var.get().strip()
        if not query:
            return

        products = get_all_products(query)
        services = get_all_services(query)

        if not products and not services:
            ctk.CTkLabel(self.item_results_frame, text="No items found.",
                         text_color="gray").pack(pady=5)
            return

        for p in products[:5]:
            row = ctk.CTkFrame(self.item_results_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"[P] {p['name']} - ₹{p['retail_price']:.2f} ({p['stock_count']} in stock)",
                         font=ctk.CTkFont(size=11)).pack(side="left")
            ctk.CTkButton(row, text="+", width=30, height=24,
                          command=lambda item=p: self.add_product_line(item)).pack(side="right")

        for s in services[:5]:
            row = ctk.CTkFrame(self.item_results_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"[S] {s['name']} - ₹{s['rate']:.2f} ({s['rate_type']})",
                         font=ctk.CTkFont(size=11)).pack(side="left")
            ctk.CTkButton(row, text="+", width=30, height=24,
                          command=lambda item=s: self.add_service_line(item)).pack(side="right")

    def add_product_line(self, product):
        self.line_items.append({
            "item_type": "product",
            "item_id": product["id"],
            "item_name": product["name"],
            "description": product["category"],
            "quantity": 1,
            "unit_price": product["retail_price"],
            "total_price": product["retail_price"],
            "maintenance_schedule": "",
        })
        self._refresh_line_items()
        self._update_totals()

    def add_service_line(self, service):
        self.line_items.append({
            "item_type": "service",
            "item_id": service["id"],
            "item_name": service["name"],
            "description": service.get("description", ""),
            "quantity": 1,
            "unit_price": service["rate"],
            "total_price": service["rate"],
            "maintenance_schedule": "",
        })
        self._refresh_line_items()
        self._update_totals()

    def _refresh_line_items(self):
        for w in self.items_display.winfo_children():
            w.destroy()

        if not self.line_items:
            ctk.CTkLabel(self.items_display, text="No items added yet.",
                         text_color="gray").pack(pady=10)
            return

        for idx, item in enumerate(self.line_items):
            row = ctk.CTkFrame(self.items_display, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)

            type_badge = "[P]" if item["item_type"] == "product" else "[S]"
            ctk.CTkLabel(row, text=f"{type_badge} {item['item_name']}",
                         font=ctk.CTkFont(size=12)).pack(side="left")

            i = idx
            ctk.CTkButton(row, text="x", width=24, height=24, fg_color="#e74c3c",
                          command=lambda ii=i: self.remove_line(ii)).pack(side="right", padx=2)

            ctk.CTkLabel(row, text=f"₹{item['total_price']:.2f}",
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=8)

            qty_frame = ctk.CTkFrame(row, fg_color="transparent")
            qty_frame.pack(side="right")
            ctk.CTkLabel(qty_frame, text="Qty:", font=ctk.CTkFont(size=11)).pack(side="left")
            qty_entry = ctk.CTkEntry(qty_frame, width=50, height=24)
            qty_entry.insert(0, str(item["quantity"]))
            qty_entry.pack(side="left", padx=2)
            qty_entry.bind("<FocusOut>", lambda e, ii=i, qe=qty_entry: self._update_qty(ii, qe))
            qty_entry.bind("<Return>", lambda e, ii=i, qe=qty_entry: self._update_qty(ii, qe))

    def _update_qty(self, idx, entry):
        try:
            qty = max(1, int(entry.get()))
        except ValueError:
            qty = 1
        self.line_items[idx]["quantity"] = qty
        self.line_items[idx]["total_price"] = qty * self.line_items[idx]["unit_price"]
        self._refresh_line_items()
        self._update_totals()

    def _update_totals(self):
        subtotal = sum(item["total_price"] for item in self.line_items)
        try:
            tax_rate = float(self.tax_var.get() or 0)
        except (ValueError, AttributeError):
            tax_rate = 0
        try:
            discount_pct = float(self.discount_var.get() or 0)
        except (ValueError, AttributeError):
            discount_pct = 0

        discount_amt = subtotal * (discount_pct / 100)
        after_discount = subtotal - discount_amt
        tax_amt = after_discount * (tax_rate / 100)
        total = after_discount + tax_amt

        self.totals_label.configure(
            text=f"Subtotal: ₹{subtotal:,.2f}  |  "
                 f"Discount: -₹{discount_amt:,.2f}  |  "
                 f"Tax: ₹{tax_amt:,.2f}  |  "
                 f"Total: ₹{total:,.2f}"
        )

    def remove_line(self, idx):
        self.line_items.pop(idx)
        self._refresh_line_items()
        self._update_totals()

    def save_invoice(self):
        if not self.line_items:
            messagebox.showwarning("Validation", "Add at least one item.")
            return

        client_sel = self.client_combo.get()
        client_id = None
        if client_sel and client_sel != "-- Walk-in --":
            try:
                client_id = int(client_sel.split(":")[0])
            except ValueError:
                pass

        subtotal = sum(item["total_price"] for item in self.line_items)
        try:
            tax_rate = float(self.tax_var.get() or 0)
        except ValueError:
            tax_rate = 0
        try:
            discount_pct = float(self.discount_var.get() or 0)
        except ValueError:
            discount_pct = 0

        discount_amt = subtotal * (discount_pct / 100)
        after_discount = subtotal - discount_amt
        tax_amt = after_discount * (tax_rate / 100)
        total = after_discount + tax_amt

        notes = self.notes_var.get("1.0", "end-1c").strip()

        tx_id = create_transaction(
            client_id=client_id, total_amount=total, subtotal=subtotal,
            tax_rate=tax_rate, tax_amount=tax_amt,
            discount_percent=discount_pct, discount_amount=discount_amt,
            tx_type="Invoice", status="Pending", notes=notes, items=self.line_items,
        )

        for item in self.line_items:
            if item["item_type"] == "product":
                decrement_stock(item["item_id"], item["quantity"])

        messagebox.showinfo("Success", f"Invoice INV-{tx_id:04d} created!")
        self.refresh_list()
        self._show_empty_detail()

    # ── View / Actions ────────────────────────────────────────

    def view_invoice(self, inv_id):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        tx = get_transaction(inv_id)
        items = get_transaction_items(inv_id)

        if not tx:
            return

        detail = ctk.CTkScrollableFrame(self.detail_frame, fg_color="transparent")
        detail.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(detail, text=f"Invoice #{tx['id']:04d}",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=(10, 2))

        status_color = "#27ae60" if tx["status"] == "Paid" else "#e67e22"
        ctk.CTkLabel(detail, text=f"Client: {tx.get('client_name', 'Walk-in')}  |  "
                     f"Date: {tx['date']}  |  Status: {tx['status']}",
                     font=ctk.CTkFont(size=12), text_color=status_color).pack(anchor="w", padx=10)

        for item in items:
            row = ctk.CTkFrame(detail, corner_radius=6)
            row.pack(fill="x", padx=10, pady=2)
            tag = "[P]" if item["item_type"] == "product" else "[S]"
            ctk.CTkLabel(row, text=f"{tag} {item['item_name']}  x{item['quantity']}",
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=f"₹{item['total_price']:,.2f}",
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=8, pady=6)

        totals_frame = ctk.CTkFrame(detail, corner_radius=8)
        totals_frame.pack(fill="x", padx=10, pady=10)

        lines = [("Subtotal", f"₹{tx['subtotal']:,.2f}")]
        if tx.get("discount_percent", 0) > 0:
            lines.append((f"Discount ({tx['discount_percent']}%)", f"-₹{tx['discount_amount']:,.2f}"))
        if tx.get("tax_rate", 0) > 0:
            lines.append((f"GST ({tx['tax_rate']}%)", f"₹{tx['tax_amount']:,.2f}"))
        lines.append(("Total", f"₹{tx['total_amount']:,.2f}"))

        for label, value in lines:
            r = ctk.CTkFrame(totals_frame, fg_color="transparent")
            r.pack(fill="x", padx=10, pady=1)
            weight = "bold" if label == "Total" else "normal"
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=12, weight=weight)).pack(side="left")
            ctk.CTkLabel(r, text=value, font=ctk.CTkFont(size=12, weight=weight)).pack(side="right")

        btn_frame = ctk.CTkFrame(detail, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)

        if self.user.has_permission("Export_PDF"):
            ctk.CTkButton(btn_frame, text="Export PDF", fg_color="#8e44ad",
                          command=lambda: self.export_pdf(inv_id)).pack(side="left", padx=(0, 5))
        if tx["status"] == "Pending":
            ctk.CTkButton(btn_frame, text="Mark as Paid", fg_color="#27ae60",
                          command=lambda: self.mark_paid(inv_id)).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Back", fg_color="gray40",
                      command=self._show_empty_detail).pack(side="left", padx=5)

    def export_pdf(self, inv_id):
        tx = get_transaction(inv_id)
        items = get_transaction_items(inv_id)
        if tx and items:
            path = generate_transaction_pdf(tx, items)
            messagebox.showinfo("PDF Exported", f"Saved to:\n{path}")
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif sys.platform == "win32":
                os.startfile(path)

    def mark_paid(self, inv_id):
        update_transaction_status(inv_id, "Paid")
        self.refresh_list()
        self._show_empty_detail()

    def del_invoice(self, inv_id):
        if messagebox.askyesno("Confirm", "Delete this invoice?"):
            delete_transaction(inv_id)
            self.refresh_list()
            self._show_empty_detail()
