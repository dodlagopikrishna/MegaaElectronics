from database_setup import get_connection
from datetime import datetime


# ── Products ──────────────────────────────────────────────────────────

def get_all_products(search=""):
    conn = get_connection()
    if search:
        rows = conn.execute(
            "SELECT * FROM products WHERE name LIKE ? OR category LIKE ? ORDER BY name",
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product(product_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(name, category, cost_price, retail_price, stock_count, unit):
    conn = get_connection()
    conn.execute(
        "INSERT INTO products (name, category, cost_price, retail_price, stock_count, unit) VALUES (?,?,?,?,?,?)",
        (name, category, cost_price, retail_price, stock_count, unit),
    )
    conn.commit()
    conn.close()


def update_product(product_id, name, category, cost_price, retail_price, stock_count, unit):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET name=?, category=?, cost_price=?, retail_price=?, stock_count=?, unit=? WHERE id=?",
        (name, category, cost_price, retail_price, stock_count, unit, product_id),
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def decrement_stock(product_id, quantity):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET stock_count = MAX(0, stock_count - ?) WHERE id = ?",
        (quantity, product_id),
    )
    conn.commit()
    conn.close()


# ── Services ──────────────────────────────────────────────────────────

def get_all_services(search=""):
    conn = get_connection()
    if search:
        rows = conn.execute(
            "SELECT * FROM services WHERE name LIKE ? OR service_type LIKE ? ORDER BY name",
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM services ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_service(service_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM services WHERE id = ?", (service_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_service(name, description, rate, rate_type, service_type):
    conn = get_connection()
    conn.execute(
        "INSERT INTO services (name, description, rate, rate_type, service_type) VALUES (?,?,?,?,?)",
        (name, description, rate, rate_type, service_type),
    )
    conn.commit()
    conn.close()


def update_service(service_id, name, description, rate, rate_type, service_type):
    conn = get_connection()
    conn.execute(
        "UPDATE services SET name=?, description=?, rate=?, rate_type=?, service_type=? WHERE id=?",
        (name, description, rate, rate_type, service_type, service_id),
    )
    conn.commit()
    conn.close()


def delete_service(service_id):
    conn = get_connection()
    conn.execute("DELETE FROM services WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()


# ── Clients ───────────────────────────────────────────────────────────

def get_all_clients(search=""):
    conn = get_connection()
    if search:
        rows = conn.execute(
            "SELECT * FROM clients WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? ORDER BY name",
            (f"%{search}%", f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_client(client_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_client(name, phone, email, address):
    conn = get_connection()
    conn.execute(
        "INSERT INTO clients (name, phone, email, address) VALUES (?,?,?,?)",
        (name, phone, email, address),
    )
    conn.commit()
    conn.close()


def update_client(client_id, name, phone, email, address):
    conn = get_connection()
    conn.execute(
        "UPDATE clients SET name=?, phone=?, email=?, address=? WHERE id=?",
        (name, phone, email, address, client_id),
    )
    conn.commit()
    conn.close()


def delete_client(client_id):
    conn = get_connection()
    conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()


# ── Transactions ──────────────────────────────────────────────────────

def get_all_transactions(search="", tx_type=None):
    conn = get_connection()
    query = """
        SELECT t.*, c.name as client_name
        FROM transactions t
        LEFT JOIN clients c ON t.client_id = c.id
        WHERE 1=1
    """
    params = []

    if tx_type:
        query += " AND t.type = ?"
        params.append(tx_type)

    if search:
        query += " AND (c.name LIKE ? OR t.id LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY t.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_transaction(tx_id):
    conn = get_connection()
    row = conn.execute(
        """SELECT t.*, c.name as client_name, c.phone as client_phone,
                  c.email as client_email, c.address as client_address
           FROM transactions t
           LEFT JOIN clients c ON t.client_id = c.id
           WHERE t.id = ?""",
        (tx_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_transaction_items(tx_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transaction_items WHERE transaction_id = ? ORDER BY id",
        (tx_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_transaction(client_id, total_amount, subtotal, tax_rate, tax_amount,
                       discount_percent, discount_amount, tx_type, status, notes, items):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO transactions
           (client_id, date, total_amount, subtotal, tax_rate, tax_amount,
            discount_percent, discount_amount, type, status, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (client_id, datetime.now().strftime("%Y-%m-%d"), total_amount, subtotal,
         tax_rate, tax_amount, discount_percent, discount_amount, tx_type, status, notes),
    )
    tx_id = cursor.lastrowid

    for item in items:
        cursor.execute(
            """INSERT INTO transaction_items
               (transaction_id, item_type, item_id, item_name, description,
                quantity, unit_price, total_price, maintenance_schedule)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (tx_id, item["item_type"], item["item_id"], item["item_name"],
             item.get("description", ""), item["quantity"], item["unit_price"],
             item["total_price"], item.get("maintenance_schedule", "")),
        )

    conn.commit()
    conn.close()
    return tx_id


def update_transaction(tx_id, client_id, total_amount, subtotal, tax_rate, tax_amount,
                       discount_percent, discount_amount, notes, items):
    """Update an existing estimate and replace its line items."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE transactions SET
           client_id=?, total_amount=?, subtotal=?, tax_rate=?, tax_amount=?,
           discount_percent=?, discount_amount=?, notes=?
           WHERE id=? AND type='Estimate'""",
        (client_id, total_amount, subtotal, tax_rate, tax_amount,
         discount_percent, discount_amount, notes, tx_id),
    )
    if cursor.rowcount == 0:
        conn.close()
        return False

    cursor.execute("DELETE FROM transaction_items WHERE transaction_id = ?", (tx_id,))
    for item in items:
        cursor.execute(
            """INSERT INTO transaction_items
               (transaction_id, item_type, item_id, item_name, description,
                quantity, unit_price, total_price, maintenance_schedule)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (tx_id, item["item_type"], item["item_id"], item["item_name"],
             item.get("description", ""), item["quantity"], item["unit_price"],
             item["total_price"], item.get("maintenance_schedule", "")),
        )

    conn.commit()
    conn.close()
    return True


def update_transaction_status(tx_id, status):
    conn = get_connection()
    conn.execute("UPDATE transactions SET status = ? WHERE id = ?", (status, tx_id))
    conn.commit()
    conn.close()


def convert_estimate_to_invoice(tx_id):
    conn = get_connection()
    conn.execute(
        "UPDATE transactions SET type = 'Invoice', status = 'Pending' WHERE id = ?",
        (tx_id,),
    )
    conn.commit()

    items = get_transaction_items(tx_id)
    for item in items:
        if item["item_type"] == "product":
            decrement_stock(item["item_id"], item["quantity"])

    conn.close()


def delete_transaction(tx_id):
    conn = get_connection()
    conn.execute("DELETE FROM transaction_items WHERE transaction_id = ?", (tx_id,))
    conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()


# ── Dashboard Stats ───────────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_connection()
    stats = {}

    row = conn.execute(
        "SELECT COALESCE(SUM(total_amount), 0) as total FROM transactions WHERE type='Invoice' AND status='Paid'"
    ).fetchone()
    stats["total_sales"] = row["total"]

    row = conn.execute(
        "SELECT COALESCE(SUM(total_amount), 0) as total FROM transactions WHERE status='Pending'"
    ).fetchone()
    stats["pending_amount"] = row["total"]

    row = conn.execute("SELECT COUNT(*) as cnt FROM transactions WHERE type='Invoice'").fetchone()
    stats["total_invoices"] = row["cnt"]

    row = conn.execute("SELECT COUNT(*) as cnt FROM transactions WHERE type='Estimate'").fetchone()
    stats["total_estimates"] = row["cnt"]

    low_stock = conn.execute(
        "SELECT * FROM products WHERE stock_count <= 5 ORDER BY stock_count ASC"
    ).fetchall()
    stats["low_stock"] = [dict(r) for r in low_stock]

    maintenance = conn.execute(
        """SELECT ti.maintenance_schedule, ti.item_name, t.id as tx_id, c.name as client_name
           FROM transaction_items ti
           JOIN transactions t ON ti.transaction_id = t.id
           LEFT JOIN clients c ON t.client_id = c.id
           WHERE ti.maintenance_schedule != '' AND ti.maintenance_schedule IS NOT NULL
           ORDER BY ti.maintenance_schedule"""
    ).fetchall()
    stats["maintenance_reminders"] = [dict(r) for r in maintenance]

    row = conn.execute("SELECT COUNT(*) as cnt FROM clients").fetchone()
    stats["total_clients"] = row["cnt"]

    conn.close()
    return stats
