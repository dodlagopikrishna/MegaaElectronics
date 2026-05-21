from nicegui import ui

from models import get_dashboard_stats
from ui_theme import page_shell, page_scroll_body, card, stat_cards_grid, stat_card, PRIMARY, SUCCESS


def render_dashboard():
    stats = get_dashboard_stats()
    content = page_shell("Dashboard")

    with content:
        with page_scroll_body():
            with stat_cards_grid():
                stat_card("Total Sales", f"₹{stats['total_sales']:,.2f}", SUCCESS)
                stat_card("Pending", f"₹{stats['pending_amount']:,.2f}", "#e67e22")
                stat_card("Invoices", str(stats["total_invoices"]), PRIMARY)
                stat_card("Estimates", str(stats["total_estimates"]), "#8b5cf6")

            with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2"):
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
                                ui.label(f"{r['client_name'] or 'N/A'} — {r['item_name']}")
                                ui.label(r["maintenance_schedule"]).classes("text-blue-500")
                    else:
                        ui.label("No upcoming maintenance").classes("text-sm text-gray-500")

            with card():
                ui.label(
                    f"Total Clients: {stats['total_clients']}  |  "
                    f"Low Stock Items: {len(stats['low_stock'])}  |  "
                    f"Maintenance Schedules: {len(stats['maintenance_reminders'])}"
                ).classes("text-sm text-gray-600 w-full")
