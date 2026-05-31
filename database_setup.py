import sqlite3
import os
import platform
import shutil
from datetime import datetime

from store_config import STORE_DB_FILENAME, STORE_NAME

SCHEMA_VERSION = 3

_LEGACY_APP_DATA_NAMES = ("Megaa Electronics", "MEGA Electronics")


def _get_app_data_dir():
    """Return the platform-appropriate application data directory."""
    app_name = STORE_NAME
    system = platform.system()

    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, app_name)
    elif system == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", app_name)
    else:
        return os.path.join(os.path.expanduser("~"), f".{app_name.lower().replace(' ', '_')}")


def _legacy_app_data_dir(name):
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, name)
    if system == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", name)
    return os.path.join(os.path.expanduser("~"), f".{name.lower().replace(' ', '_')}")


def _migrate_app_data_dir_if_needed(target_dir):
    """Copy data from older application support folder names."""
    if os.path.isdir(target_dir) and os.listdir(target_dir):
        return

    os.makedirs(target_dir, exist_ok=True)
    for legacy_name in _LEGACY_APP_DATA_NAMES:
        if legacy_name == STORE_NAME:
            continue
        legacy_dir = _legacy_app_data_dir(legacy_name)
        if not os.path.isdir(legacy_dir):
            continue
        for item in os.listdir(legacy_dir):
            src = os.path.join(legacy_dir, item)
            dst = os.path.join(target_dir, item)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
        return


APP_DATA_DIR = _get_app_data_dir()
_migrate_app_data_dir_if_needed(APP_DATA_DIR)
os.makedirs(APP_DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(APP_DATA_DIR, STORE_DB_FILENAME)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _get_schema_version(conn):
    if not _table_exists(conn, "app_metadata"):
        return None
    row = conn.execute(
        "SELECT value FROM app_metadata WHERE key = 'schema_version'"
    ).fetchone()
    if not row:
        return None
    try:
        return int(row["value"])
    except (TypeError, ValueError):
        return None


def _needs_schema_reset(conn):
    if _table_exists(conn, "transactions") or _table_exists(conn, "transaction_items"):
        return True
    version = _get_schema_version(conn)
    return version is None or version < SCHEMA_VERSION


def _backup_database_if_exists():
    if not os.path.isfile(DB_PATH):
        return
    backup_name = f"{STORE_DB_FILENAME}.backup-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(DB_PATH, os.path.join(APP_DATA_DIR, backup_name))


def _drop_all_tables(conn):
    """Drop every application table in FK-safe order."""
    tables = [
        "maintenance_schedules",
        "invoice_items",
        "estimate_items",
        "invoices",
        "estimates",
        "transaction_items",
        "transactions",
        "user_roles",
        "role_permissions",
        "users",
        "permissions",
        "roles",
        "clients",
        "services",
        "products",
        "app_metadata",
    ]
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")


def _create_schema(conn):
    conn.executescript("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'CCTV',
            buy_price REAL NOT NULL DEFAULT 0,
            sell_price REAL NOT NULL DEFAULT 0,
            stock_count INTEGER NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'pcs',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            rate REAL NOT NULL DEFAULT 0,
            worker_cost REAL NOT NULL DEFAULT 0,
            rate_type TEXT NOT NULL DEFAULT 'Flat Fee',
            service_type TEXT NOT NULL DEFAULT 'Installation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            address TEXT DEFAULT '',
            location TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            date TEXT NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL DEFAULT 0,
            tax_enabled INTEGER NOT NULL DEFAULT 0,
            tax_rate REAL NOT NULL DEFAULT 0,
            tax_amount REAL NOT NULL DEFAULT 0,
            discount_percent REAL NOT NULL DEFAULT 0,
            discount_amount REAL NOT NULL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE estimate_items (
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

        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            date TEXT NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL DEFAULT 0,
            tax_enabled INTEGER NOT NULL DEFAULT 0,
            tax_rate REAL NOT NULL DEFAULT 0,
            tax_amount REAL NOT NULL DEFAULT 0,
            discount_percent REAL NOT NULL DEFAULT 0,
            discount_amount REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Pending',
            source_estimate_id INTEGER,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (source_estimate_id) REFERENCES estimates(id)
        );

        CREATE TABLE invoice_items (
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

        CREATE TABLE maintenance_schedules (
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

        CREATE INDEX idx_estimates_date ON estimates(date);
        CREATE INDEX idx_invoices_date ON invoices(date);
        CREATE INDEX idx_invoices_status ON invoices(status);
        CREATE INDEX idx_invoices_date_status ON invoices(date, status);
        CREATE INDEX idx_invoices_source_estimate_id ON invoices(source_estimate_id);
        CREATE INDEX idx_estimate_items_estimate_id ON estimate_items(estimate_id);
        CREATE INDEX idx_invoice_items_invoice_id ON invoice_items(invoice_id);
        CREATE INDEX idx_maintenance_schedules_client ON maintenance_schedules(client_id);
        CREATE INDEX idx_maintenance_schedules_status ON maintenance_schedules(status);
        CREATE INDEX idx_maintenance_schedules_due ON maintenance_schedules(next_due_date);

        CREATE TABLE roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
            UNIQUE(role_id, permission_id)
        );

        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL DEFAULT '',
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role_id INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            must_change_password INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            UNIQUE(user_id, role_id)
        );

        CREATE TABLE app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        );
    """)


def _set_schema_version(conn):
    conn.execute(
        "INSERT OR REPLACE INTO app_metadata (key, value) VALUES ('schema_version', ?)",
        (str(SCHEMA_VERSION),),
    )


def initialize_database():
    conn = get_connection()
    if _needs_schema_reset(conn):
        conn.close()
        _backup_database_if_exists()
        conn = get_connection()
        _drop_all_tables(conn)
        _create_schema(conn)
        _set_schema_version(conn)
        conn.commit()
        conn.close()
        _seed_roles_and_permissions()
        return

    cursor = conn.cursor()
    cursor.executescript("""
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

        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            date TEXT NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL DEFAULT 0,
            tax_enabled INTEGER NOT NULL DEFAULT 0,
            tax_rate REAL NOT NULL DEFAULT 0,
            tax_amount REAL NOT NULL DEFAULT 0,
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

        CREATE INDEX IF NOT EXISTS idx_estimates_date ON estimates(date);
        CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(date);
        CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
        CREATE INDEX IF NOT EXISTS idx_invoices_date_status ON invoices(date, status);
        CREATE INDEX IF NOT EXISTS idx_invoices_source_estimate_id ON invoices(source_estimate_id);
        CREATE INDEX IF NOT EXISTS idx_estimate_items_estimate_id ON estimate_items(estimate_id);
        CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items(invoice_id);
        CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_client ON maintenance_schedules(client_id);
        CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_status ON maintenance_schedules(status);
        CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_due ON maintenance_schedules(next_due_date);

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
    """)
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

    roles = ["Admin", "Sales", "Inventory", "Technician"]
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
            "Dashboard", "Clients_View", "Clients_Edit",
            "Quotes_View", "Quotes_Create",
            "Invoices_View", "Invoices_Create",
            "Maintenance_View",
            "Products_View", "Services_View", "Export_PDF",
        ],
        "Inventory": [
            "Dashboard", "Products_View", "Products_Edit", "Products_Delete",
            "Services_View", "Services_Edit", "Services_Delete",
            "Stock_Edit", "Cost_Prices",
        ],
        "Technician": [
            "Dashboard", "Services_View", "Service_Complete",
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


def seed_sample_data():
    """Insert sample data for demonstration purposes."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    products = [
        ("Hikvision 2MP Bullet Camera", "CCTV", 45.00, 89.99, 25, "pcs"),
        ("Dahua 4MP Dome Camera", "CCTV", 65.00, 129.99, 18, "pcs"),
        ("Hikvision 8-Channel NVR", "CCTV", 120.00, 249.99, 10, "pcs"),
        ("Cat6 Network Cable", "Accessories", 0.30, 0.75, 500, "meters"),
        ("Epson EB-E01 Projector", "Projector", 280.00, 499.99, 8, "pcs"),
        ("BenQ MH560 Projector", "Projector", 350.00, 599.99, 5, "pcs"),
        ("Projector Ceiling Mount", "Accessories", 15.00, 35.99, 20, "pcs"),
        ("100\" Motorized Screen", "Accessories", 85.00, 179.99, 7, "pcs"),
        ("1TB Surveillance HDD", "CCTV", 35.00, 69.99, 15, "pcs"),
        ("PoE Network Switch 8-Port", "Accessories", 25.00, 54.99, 12, "pcs"),
    ]

    services = [
        ("CCTV Installation - Basic", "Up to 4 cameras, standard wiring", 150.00, 80.00, "Flat Fee", "Installation"),
        ("CCTV Installation - Advanced", "Up to 8 cameras, concealed wiring", 300.00, 160.00, "Flat Fee", "Installation"),
        ("Projector Installation", "Ceiling mount, cable routing, calibration", 120.00, 65.00, "Flat Fee", "Installation"),
        ("Network Cabling", "Per-hour structured cabling service", 45.00, 25.00, "Hourly Rate", "Installation"),
        ("CCTV Maintenance - Monthly", "Monthly inspection and cleaning", 80.00, 40.00, "Flat Fee", "Maintenance"),
        ("CCTV Maintenance - Quarterly", "Quarterly full system check", 200.00, 100.00, "Flat Fee", "Maintenance"),
        ("Projector Maintenance", "Lamp check, filter cleaning, alignment", 60.00, 30.00, "Flat Fee", "Maintenance"),
        ("Emergency Repair", "On-site emergency troubleshooting", 75.00, 40.00, "Hourly Rate", "Maintenance"),
    ]

    clients = [
        ("Acme Corporation", "+65 9123 4567", "contact@acme.sg", "123 Orchard Road, Singapore 238858", ""),
        ("Bright Office Pte Ltd", "+65 8234 5678", "admin@brightoffice.com", "456 Raffles Place, Singapore 048623", ""),
        ("City Mall Management", "+65 7345 6789", "ops@citymall.sg", "789 Jurong East St 21, Singapore 609602", ""),
    ]

    cursor.executemany(
        "INSERT INTO products (name, category, buy_price, sell_price, stock_count, unit) VALUES (?,?,?,?,?,?)",
        products,
    )
    cursor.executemany(
        "INSERT INTO services (name, description, rate, worker_cost, rate_type, service_type) VALUES (?,?,?,?,?,?)",
        services,
    )
    cursor.executemany(
        "INSERT INTO clients (name, phone, email, address, location) VALUES (?,?,?,?,?)",
        clients,
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    seed_sample_data()
    print(f"Database initialized at: {DB_PATH}")
