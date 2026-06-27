from datetime import date

from nicegui import ui

from login_manager import CurrentUser
from models import acknowledge_warranty_reminder, get_dashboard_stats, mark_maintenance_completed
from views.maintenance import format_schedule_due
from ui_theme import (
    page_shell,
    page_scroll_body,
    card,
    collapsible_stat_group,
    stat_card,
    ghost_button,
    confirm_dialog,
    PRIMARY,
    SUCCESS,
)

_DATE_INPUT = "ios-field shrink-0 w-40 sm:w-44"


def _format_warranty_expiry(warranty_expiry: str) -> str:
    expiry = date.fromisoformat(warranty_expiry)
    if expiry >= date.today():
        return f"Expires {warranty_expiry}"
    return f"Expired {warranty_expiry}"


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

                net_profit = stats["profit_products_only"] - stats["total_discounts"]
                with collapsible_stat_group(
                    "Profit",
                    f"₹{net_profit:,.2f}",
                    caption="Net profit (after discounts)",
                ):
                    with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2"):
                        stat_card(
                            "Gross Profit (products only)",
                            f"₹{stats['profit_products_only']:,.2f}",
                            "#0ea5e9",
                        )
                        stat_card(
                            "Gross Profit (services only)",
                            f"₹{stats['profit_services_only']:,.2f}",
                            PRIMARY,
                        )
                        stat_card(
                            "Total Discounts",
                            f"₹{stats['total_discounts']:,.2f}",
                            "#e67e22",
                        )
                        stat_card(
                            "Net Profit",
                            f"₹{net_profit:,.2f}",
                            SUCCESS,
                        )

                stat_card("Total Clients", str(stats["total_clients"]), "#64748b")

            with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 mt-4"):
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
                            schedule_id = r["id"]
                            client_name = r["client_name"] or "N/A"
                            service_name = r["service_name"]

                            def close_reminder(
                                schedule_id=schedule_id,
                                client_name=client_name,
                                service_name=service_name,
                            ):
                                def do_close():
                                    mark_maintenance_completed(schedule_id)
                                    load_stats()

                                confirm_dialog(
                                    "Mark as Completed",
                                    f"Mark maintenance as completed for {client_name} — {service_name}?",
                                    do_close,
                                )

                            with ui.row().classes("w-full items-center justify-between gap-2 py-1"):
                                ui.label(
                                    f"{client_name} — {service_name}"
                                ).classes("text-sm flex-grow")
                                ui.label(
                                    f"{r['frequency']} · Due: {format_schedule_due(r)}"
                                ).classes("text-sm text-blue-500 shrink-0")
                                ui.button(icon="close", on_click=close_reminder).props(
                                    "flat dense round aria-label=Mark maintenance completed"
                                ).classes("shrink-0")
                    else:
                        ui.label("No upcoming maintenance").classes("text-sm text-gray-500")

                with card():
                    ui.label("Warranty Completion Reminders").classes(
                        "text-base font-bold mb-2"
                    ).style(f"color:{PRIMARY}")
                    if stats["warranty_reminders"]:
                        for r in stats["warranty_reminders"][:10]:
                            invoice_id = r["invoice_id"]
                            client_name = r["client_name"]

                            def close_reminder(invoice_id=invoice_id, client_name=client_name):
                                def do_close():
                                    acknowledge_warranty_reminder(
                                        invoice_id, CurrentUser.get().user_id
                                    )
                                    load_stats()

                                confirm_dialog(
                                    "Close Reminder",
                                    f"Close warranty reminder for Invoice #{invoice_id} — {client_name}?",
                                    do_close,
                                )

                            with ui.row().classes("w-full items-center justify-between gap-2 py-1"):
                                ui.label(
                                    f"Invoice #{invoice_id} — {client_name}"
                                ).classes("text-sm flex-grow")
                                ui.label(
                                    _format_warranty_expiry(r["warranty_expiry"])
                                ).classes("text-sm text-blue-500 shrink-0")
                                ui.button(icon="close", on_click=close_reminder).props(
                                    "flat dense round aria-label=Close reminder"
                                ).classes("shrink-0")
                    else:
                        ui.label("No warranty reminders").classes("text-sm text-gray-500")

            with card():
                ui.label(
                    f"Low Stock Items: {len(stats['low_stock'])}  |  "
                    f"Maintenance Schedules: {len(stats['maintenance_reminders'])}  |  "
                    f"Warranty Reminders: {len(stats['warranty_reminders'])}"
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
