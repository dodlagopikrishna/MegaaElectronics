import sqlite3
import os
import sys
import platform


def _get_app_data_dir():
    """Return the platform-appropriate application data directory."""
    app_name = "MEGA Electronics"
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

DB_PATH = os.path.join(APP_DATA_DIR, "mega_electronics.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'CCTV',
            cost_price REAL NOT NULL DEFAULT 0,
            retail_price REAL NOT NULL DEFAULT 0,
            stock_count INTEGER NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'pcs',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            rate REAL NOT NULL DEFAULT 0,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            date TEXT NOT NULL,
            total_amount REAL NOT NULL DEFAULT 0,
            subtotal REAL NOT NULL DEFAULT 0,
            tax_rate REAL NOT NULL DEFAULT 0,
            tax_amount REAL NOT NULL DEFAULT 0,
            discount_percent REAL NOT NULL DEFAULT 0,
            discount_amount REAL NOT NULL DEFAULT 0,
            type TEXT NOT NULL DEFAULT 'Estimate',
            status TEXT NOT NULL DEFAULT 'Pending',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            item_type TEXT NOT NULL DEFAULT 'product',
            item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL DEFAULT 0,
            total_price REAL NOT NULL DEFAULT 0,
            maintenance_schedule TEXT DEFAULT '',
            FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
        );

        -- Authentication & RBAC tables

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
    """)

    conn.commit()
    conn.close()

    _seed_roles_and_permissions()
    _migrate_to_multi_roles()


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
            "Products_View", "Services_View", "Export_PDF",
        ],
        "Inventory": [
            "Dashboard", "Products_View", "Products_Edit", "Products_Delete",
            "Services_View", "Services_Edit", "Services_Delete",
            "Stock_Edit", "Cost_Prices",
        ],
        "Technician": [
            "Dashboard", "Services_View", "Service_Complete",
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


def _migrate_to_multi_roles():
    """Migrate existing users with role_id to the user_roles junction table."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT u.id, u.role_id FROM users u
           WHERE u.role_id > 0
             AND u.id NOT IN (SELECT user_id FROM user_roles)"""
    )
    orphans = cursor.fetchall()
    for row in orphans:
        cursor.execute(
            "INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)",
            (row["id"], row["role_id"]),
        )

    if orphans:
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
        ("CCTV Installation - Basic", "Up to 4 cameras, standard wiring", 150.00, "Flat Fee", "Installation"),
        ("CCTV Installation - Advanced", "Up to 8 cameras, concealed wiring", 300.00, "Flat Fee", "Installation"),
        ("Projector Installation", "Ceiling mount, cable routing, calibration", 120.00, "Flat Fee", "Installation"),
        ("Network Cabling", "Per-hour structured cabling service", 45.00, "Hourly Rate", "Installation"),
        ("CCTV Maintenance - Monthly", "Monthly inspection and cleaning", 80.00, "Flat Fee", "Maintenance"),
        ("CCTV Maintenance - Quarterly", "Quarterly full system check", 200.00, "Flat Fee", "Maintenance"),
        ("Projector Maintenance", "Lamp check, filter cleaning, alignment", 60.00, "Flat Fee", "Maintenance"),
        ("Emergency Repair", "On-site emergency troubleshooting", 75.00, "Hourly Rate", "Maintenance"),
    ]

    clients = [
        ("Acme Corporation", "+65 9123 4567", "contact@acme.sg", "123 Orchard Road, Singapore 238858"),
        ("Bright Office Pte Ltd", "+65 8234 5678", "admin@brightoffice.com", "456 Raffles Place, Singapore 048623"),
        ("City Mall Management", "+65 7345 6789", "ops@citymall.sg", "789 Jurong East St 21, Singapore 609602"),
    ]

    cursor.executemany(
        "INSERT INTO products (name, category, cost_price, retail_price, stock_count, unit) VALUES (?,?,?,?,?,?)",
        products,
    )
    cursor.executemany(
        "INSERT INTO services (name, description, rate, rate_type, service_type) VALUES (?,?,?,?,?)",
        services,
    )
    cursor.executemany(
        "INSERT INTO clients (name, phone, email, address) VALUES (?,?,?,?)",
        clients,
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    seed_sample_data()
    print(f"Database initialized at: {DB_PATH}")
