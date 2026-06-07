import sqlite3
import os
import platform

from app_config import get_db_dir
from store_config import STORE_DB_FILENAME, STORE_NAME

SCHEMA_VERSION = 2


def _get_app_data_dir():
    """Return the application data directory.

    Uses the path from config.json (written by the installer) when available,
    otherwise falls back to the platform-appropriate default.
    """
    configured = get_db_dir()
    if configured:
        return configured

    app_name = STORE_NAME
    system = platform.system()

    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, app_name)
    elif system == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", app_name)
    else:
        return os.path.join(os.path.expanduser("~"), f".{app_name.lower().replace(' ', '_')}")


APP_DATA_DIR = _get_app_data_dir()
os.makedirs(APP_DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(APP_DATA_DIR, STORE_DB_FILENAME)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'CCTV',
            buy_price REAL NOT NULL DEFAULT 0,
            sell_price REAL NOT NULL DEFAULT 0,
            stock_count INTEGER NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'pcs',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            rate REAL NOT NULL DEFAULT 0,
            worker_cost REAL NOT NULL DEFAULT 0,
            rate_type TEXT NOT NULL DEFAULT 'Flat Fee',
            service_type TEXT NOT NULL DEFAULT 'Installation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            address TEXT DEFAULT '',
            location TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS client_referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL UNIQUE
                REFERENCES clients(id) ON DELETE CASCADE,
            referrer_client_id INTEGER NOT NULL
                REFERENCES clients(id) ON DELETE RESTRICT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (client_id != referrer_client_id)
        );

        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            date TEXT NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL DEFAULT 0,
            tax_enabled INTEGER NOT NULL DEFAULT 0,
            tax_rate REAL NOT NULL DEFAULT 0,
            tax_amount REAL NOT NULL DEFAULT 0,
            discount_type TEXT NOT NULL DEFAULT 'flat',
            discount_percent REAL NOT NULL DEFAULT 0,
            discount_amount REAL NOT NULL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS estimate_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estimate_id INTEGER NOT NULL,
            item_type TEXT NOT NULL DEFAULT 'product',
            item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL DEFAULT 0,
            unit_cost REAL NOT NULL DEFAULT 0,
            total_price REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (estimate_id) REFERENCES estimates(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            date TEXT NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL DEFAULT 0,
            tax_enabled INTEGER NOT NULL DEFAULT 0,
            tax_rate REAL NOT NULL DEFAULT 0,
            tax_amount REAL NOT NULL DEFAULT 0,
            discount_type TEXT NOT NULL DEFAULT 'flat',
            discount_percent REAL NOT NULL DEFAULT 0,
            discount_amount REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Pending',
            source_estimate_id INTEGER,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (source_estimate_id) REFERENCES estimates(id)
        );

        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            item_type TEXT NOT NULL DEFAULT 'product',
            item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL DEFAULT 0,
            unit_cost REAL NOT NULL DEFAULT 0,
            total_price REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS maintenance_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            frequency TEXT NOT NULL DEFAULT 'Monthly',
            start_date TEXT NOT NULL,
            next_due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
            UNIQUE(role_id, permission_id)
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL DEFAULT '',
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT '',
            role_id INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            must_change_password INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            UNIQUE(user_id, role_id)
        );

        CREATE TABLE IF NOT EXISTS app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        );

        CREATE INDEX IF NOT EXISTS idx_estimates_date ON estimates(date);
        CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(date);
        CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
        CREATE INDEX IF NOT EXISTS idx_invoices_date_status ON invoices(date, status);
        CREATE INDEX IF NOT EXISTS idx_invoices_source_estimate_id ON invoices(source_estimate_id);
        CREATE INDEX IF NOT EXISTS idx_estimate_items_estimate_id ON estimate_items(estimate_id);
        CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items(invoice_id);
        CREATE INDEX IF NOT EXISTS idx_client_referrals_referrer ON client_referrals(referrer_client_id);
        CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_client ON maintenance_schedules(client_id);
        CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_status ON maintenance_schedules(status);
        CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_due ON maintenance_schedules(next_due_date);
    """)
    conn.execute(
        "INSERT OR REPLACE INTO app_metadata (key, value) VALUES ('schema_version', ?)",
        (str(SCHEMA_VERSION),),
    )
    conn.commit()
    conn.close()

    _seed_roles_and_permissions()



def _seed_roles_and_permissions():
    """Insert default roles, permissions, and role-permission mappings if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    roles = ["Admin", "Sales", "Technician"]
    for role in roles:
        cursor.execute("INSERT INTO roles (role_name) VALUES (?)", (role,))

    all_permissions = [
        "Dashboard", "Products_View", "Products_Edit", "Products_Delete",
        "Services_View", "Services_Edit", "Services_Delete",
        "Clients_View", "Clients_Edit", "Clients_Delete",
        "Quotes_View", "Quotes_Create", "Quotes_Delete",
        "Invoices_View", "Invoices_Create", "Invoices_Delete",
        "Maintenance_View", "Maintenance_Edit", "Maintenance_Delete",
        "Cost_Prices", "Financials", "Stock_Edit",
        "User_Management", "Export_PDF", "Service_Complete",
    ]
    for perm in all_permissions:
        cursor.execute("INSERT INTO permissions (module_name) VALUES (?)", (perm,))

    role_permission_map = {
        "Admin": all_permissions,
        "Sales": [
            "Products_View", "Products_Edit", "Products_Delete",
            "Services_View", "Services_Edit", "Services_Delete",
            "Stock_Edit", "Cost_Prices",
            "Clients_View", "Clients_Edit", "Clients_Delete",
            "Quotes_View", "Quotes_Create", "Quotes_Delete",
            "Invoices_View", "Invoices_Create",
            "Maintenance_View", "Maintenance_Edit", "Maintenance_Delete",
            "Export_PDF", "Financials",
        ],
        "Technician": [
            "Maintenance_View", "Maintenance_Edit",
        ],
    }

    for role_name, perms in role_permission_map.items():
        cursor.execute("SELECT id FROM roles WHERE role_name = ?", (role_name,))
        role_id = cursor.fetchone()["id"]
        for perm_name in perms:
            cursor.execute("SELECT id FROM permissions WHERE module_name = ?", (perm_name,))
            perm_row = cursor.fetchone()
            if perm_row:
                cursor.execute(
                    "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                    (role_id, perm_row["id"]),
                )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DB_PATH}")
