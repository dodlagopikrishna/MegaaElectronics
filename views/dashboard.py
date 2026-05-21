import customtkinter as ctk
from models import get_dashboard_stats
from responsive_ui import ResponsiveDashboardLayout


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._card_layout = None
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkLabel(
            self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(anchor="w", padx=20, pady=(20, 10))

        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.details_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.details_frame.bind("<Configure>", self._on_details_resize, add="+")

        self._cards_layout = ResponsiveDashboardLayout(self.cards_frame, self.details_frame)
        self.refresh()

    def _on_details_resize(self, _event=None):
        if not hasattr(self, "_low_stock_frame"):
            return
        w = self.details_frame.winfo_width()
        if w < 2:
            return
        if hasattr(self, "_quick_label"):
            self._quick_label.configure(wraplength=max(200, w - 40))
        mode = self._cards_layout.layout_details(w)
        if mode == "stack":
            self._low_stock_frame.grid(
                row=0, column=0, padx=8, pady=8, sticky="nsew"
            )
            self._maint_frame.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
            self._quick_frame.grid(
                row=2, column=0, columnspan=1, padx=8, pady=8, sticky="nsew"
            )
        else:
            self._low_stock_frame.grid(
                row=0, column=0, padx=8, pady=8, sticky="nsew"
            )
            self._maint_frame.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
            self._quick_frame.grid(
                row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew"
            )

    def refresh(self):
        for w in self.details_frame.winfo_children():
            w.destroy()

        stats = get_dashboard_stats()

        cards = [
            ("Total Sales", f"₹{stats['total_sales']:,.2f}", "#27ae60"),
            ("Pending", f"₹{stats['pending_amount']:,.2f}", "#e67e22"),
            ("Invoices", str(stats["total_invoices"]), "#2980b9"),
            ("Estimates", str(stats["total_estimates"]), "#8e44ad"),
        ]
        self._cards_layout.set_cards(cards)

        self.details_frame.grid_rowconfigure(0, weight=1)
        self.details_frame.grid_rowconfigure(1, weight=1)

        self._low_stock_frame = ctk.CTkFrame(self.details_frame, corner_radius=12)
        ctk.CTkLabel(
            self._low_stock_frame,
            text="Low Stock Alerts",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e74c3c",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        if stats["low_stock"]:
            for item in stats["low_stock"]:
                row = ctk.CTkFrame(self._low_stock_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=2)
                ctk.CTkLabel(row, text=f"  {item['name']}", font=ctk.CTkFont(size=12)).pack(
                    side="left"
                )
                badge_color = "#e74c3c" if item["stock_count"] <= 2 else "#e67e22"
                ctk.CTkLabel(
                    row,
                    text=f" {item['stock_count']} left ",
                    font=ctk.CTkFont(size=11),
                    corner_radius=6,
                    fg_color=badge_color,
                    text_color="white",
                ).pack(side="right", padx=5)
        else:
            ctk.CTkLabel(
                self._low_stock_frame,
                text="  All items well stocked",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            ).pack(anchor="w", padx=15, pady=5)

        self._maint_frame = ctk.CTkFrame(self.details_frame, corner_radius=12)
        ctk.CTkLabel(
            self._maint_frame,
            text="Maintenance Reminders",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2980b9",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        reminders = stats["maintenance_reminders"]
        if reminders:
            for r in reminders[:10]:
                row = ctk.CTkFrame(self._maint_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=2)
                ctk.CTkLabel(
                    row,
                    text=f"  {r['client_name'] or 'N/A'} - {r['item_name']}",
                    font=ctk.CTkFont(size=12),
                ).pack(side="left")
                ctk.CTkLabel(
                    row,
                    text=r["maintenance_schedule"],
                    font=ctk.CTkFont(size=11),
                    text_color="#2980b9",
                ).pack(side="right", padx=5)
        else:
            ctk.CTkLabel(
                self._maint_frame,
                text="  No upcoming maintenance",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            ).pack(anchor="w", padx=15, pady=5)

        self._quick_frame = ctk.CTkFrame(self.details_frame, corner_radius=12)
        quick_text = (
            f"Total Clients: {stats['total_clients']}  |  "
            f"Total Products with Low Stock: {len(stats['low_stock'])}  |  "
            f"Maintenance Schedules: {len(stats['maintenance_reminders'])}"
        )
        self._quick_label = ctk.CTkLabel(
            self._quick_frame,
            text=quick_text,
            font=ctk.CTkFont(size=12),
            wraplength=600,
        )
        self._quick_label.pack(padx=15, pady=12)

        self.details_frame.after_idle(self._on_details_resize)
