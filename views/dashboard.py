from datetime import date

from nicegui import ui

from models import get_dashboard_stats
from views.maintenance import format_schedule_due
from ui_theme import (
    page_shell,
    page_scroll_body,
    card,
    collapsible_stat_group,
    stat_card,
    ghost_button,
    PRIMARY,
    SUCCESS,
)

_DATE_INPUT = "ios-field shrink-0 w-40 sm:w-44"


def render_dashboard():
    today = date.today()
    date_from_default = today.replace(day=1).isoformat()
    date_to_default = today.isoformat()
    state = {"date_from": date_from_default, "date_to": date_to_default}
    stats_container = None

    def load_stats():
        stats = get_dashboard_stats(state["date_from"], state["date_to"])
        stats_container.clear()
        with stats_container:
            sales_total = stats["sales_paid_total"] + stats["sales_pending_total"]
            sales_count = stats["sales_paid_count"] + stats["sales_pending_count"]

            with ui.column().classes("w-full gap-3"):
                with collapsible_stat_group(
                    "Sales",
                    f"₹{sales_total:,.2f}",
                    caption=f"{sales_count} invoices",
                ):
                    with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2"):
                        stat_card(
                            "Sales (Paid)",
                            f"₹{stats['sales_paid_total']:,.2f}",
                            SUCCESS,
                            subtitle=f"{stats['sales_paid_count']} invoices",
                        )
                        stat_card(
                            "Sales (Pending)",
                            f"₹{stats['sales_pending_total']:,.2f}",
                            "#e67e22",
                            subtitle=f"{stats['sales_pending_count']} invoices",
                        )

                with collapsible_stat_group(
                    "Estimates",
                    f"₹{stats['estimates_total']:,.2f}",
                    caption=f"{stats['estimates_count']} estimates",
                ):
                    stat_card(
                        "Estimates",
                        f"₹{stats['estimates_total']:,.2f}",
                        "#8b5cf6",
                        subtitle=f"{stats['estimates_count']} estimates",
                    )

                with collapsible_stat_group(
                    "Profit",
                    f"₹{stats['profit_with_services']:,.2f}",
                    caption="incl. services",
                ):
                    with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2"):
                        stat_card(
                            "Profit (products only)",
                            f"₹{stats['profit_products_only']:,.2f}",
                            "#0ea5e9",
                        )
                        stat_card(
                            "Profit (incl. services)",
                            f"₹{stats['profit_with_services']:,.2f}",
                            PRIMARY,
                        )

                stat_card("Total Clients", str(stats["total_clients"]), "#64748b")

            with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2 mt-4"):
                with card():
                    ui.label("Low Stock Alerts").classes("text-base font-bold text-red-500 mb-2")
                    if stats["low_stock"]:
                        for item in stats["low_stock"]:
                            with ui.row().classes("w-full justify-between py-1"):
                                ui.label(item["name"]).classes("text-sm")
                                color = "red" if item["stock_count"] <= 2 else "orange"
                                ui.badge(f"{item['stock_count']} left").props(f"color={color}")
                    else:
                        ui.label("All items well stocked").classes("text-sm text-gray-500")

                with card():
                    ui.label("Maintenance Reminders").classes("text-base font-bold mb-2").style(
                        f"color:{PRIMARY}"
                    )
                    if stats["maintenance_reminders"]:
                        for r in stats["maintenance_reminders"][:10]:
                            with ui.row().classes("w-full justify-between py-1 text-sm"):
                                ui.label(f"{r['client_name'] or 'N/A'} — {r['service_name']}")
                                ui.label(
                                    f"{r['frequency']} · Due: {format_schedule_due(r)}"
                                ).classes("text-blue-500")
                    else:
                        ui.label("No upcoming maintenance").classes("text-sm text-gray-500")

            with card():
                ui.label(
                    f"Low Stock Items: {len(stats['low_stock'])}  |  "
                    f"Maintenance Schedules: {len(stats['maintenance_reminders'])}"
                ).classes("text-sm text-gray-600 w-full")

    content = page_shell("Dashboard")
    with content:
        with page_scroll_body():
            with card().classes("mb-4"):
                with ui.row().classes("w-full items-end gap-3 flex-nowrap"):
                    date_from_inp = ui.input("From", value=date_from_default).props(
                        "outlined dense type=date"
                    ).classes(_DATE_INPUT)
                    date_to_inp = ui.input("To", value=date_to_default).props(
                        "outlined dense type=date"
                    ).classes(_DATE_INPUT)

                    def apply_dates():
                        state["date_from"] = date_from_inp.value or date_from_default
                        state["date_to"] = date_to_inp.value or date_to_default
                        load_stats()

                    ghost_button("Apply", on_click=apply_dates)

            stats_container = ui.column().classes("w-full gap-4")
            load_stats()
