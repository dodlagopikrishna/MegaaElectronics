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


def add_product(name, category, buy_price, sell_price, stock_count, unit):
    conn = get_connection()
    conn.execute(
        "INSERT INTO products (name, category, buy_price, sell_price, stock_count, unit) VALUES (?,?,?,?,?,?)",
        (name, category, buy_price, sell_price, stock_count, unit),
    )
    conn.commit()
    conn.close()


def update_product(product_id, name, category, buy_price, sell_price, stock_count, unit):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET name=?, category=?, buy_price=?, sell_price=?, stock_count=?, unit=? WHERE id=?",
        (name, category, buy_price, sell_price, stock_count, unit, product_id),
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


def increment_stock(product_id, quantity):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET stock_count = stock_count + ? WHERE id = ?",
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


def add_service(name, description, rate, worker_cost, rate_type, service_type):
    conn = get_connection()
    conn.execute(
        "INSERT INTO services (name, description, rate, worker_cost, rate_type, service_type) VALUES (?,?,?,?,?,?)",
        (name, description, rate, worker_cost, rate_type, service_type),
    )
    conn.commit()
    conn.close()


def update_service(service_id, name, description, rate, worker_cost, rate_type, service_type):
    conn = get_connection()
    conn.execute(
        "UPDATE services SET name=?, description=?, rate=?, worker_cost=?, rate_type=?, service_type=? WHERE id=?",
        (name, description, rate, worker_cost, rate_type, service_type, service_id),
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


def add_client(name, phone, email, address, location=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO clients (name, phone, email, address, location) VALUES (?,?,?,?,?)",
        (name, phone, email, address, location),
    )
    conn.commit()
    conn.close()


def update_client(client_id, name, phone, email, address, location=""):
    conn = get_connection()
    conn.execute(
        "UPDATE clients SET name=?, phone=?, email=?, address=?, location=? WHERE id=?",
        (name, phone, email, address, location, client_id),
    )
    conn.commit()
    conn.close()


def delete_client(client_id):
    conn = get_connection()
    conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()


# ── Line item helpers ─────────────────────────────────────────────────

def _unit_cost_for_item(item_type, item_id):
    if item_type == "product":
        product = get_product(item_id)
        return product["buy_price"] if product else 0
    service = get_service(item_id)
    return service["worker_cost"] if service else 0


def _normalize_item(item):
    normalized = dict(item)
    if "unit_cost" not in normalized or normalized.get("unit_cost") is None:
        normalized["unit_cost"] = _unit_cost_for_item(
            normalized["item_type"], normalized["item_id"]
        )
    return normalized


def _insert_estimate_items(cursor, estimate_id, items):
    for item in items:
        item = _normalize_item(item)
        cursor.execute(
            """INSERT INTO estimate_items
               (estimate_id, item_type, item_id, item_name, description,
                quantity, unit_price, unit_cost, total_price)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                estimate_id,
                item["item_type"],
                item["item_id"],
                item["item_name"],
                item.get("description", ""),
                item["quantity"],
                item["unit_price"],
                item["unit_cost"],
                item["total_price"],
            ),
        )


def _insert_invoice_items(cursor, invoice_id, items):
    for item in items:
        item = _normalize_item(item)
        cursor.execute(
            """INSERT INTO invoice_items
               (invoice_id, item_type, item_id, item_name, description,
                quantity, unit_price, unit_cost, total_price)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                invoice_id,
                item["item_type"],
                item["item_id"],
                item["item_name"],
                item.get("description", ""),
                item["quantity"],
                item["unit_price"],
                item["unit_cost"],
                item["total_price"],
            ),
        )


# ── Estimates ─────────────────────────────────────────────────────────

_OPEN_ESTIMATE_SQL = """
AND NOT EXISTS (
  SELECT 1 FROM invoices i WHERE i.source_estimate_id = e.id
)
"""


def estimate_is_converted(estimate_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM invoices WHERE source_estimate_id = ? LIMIT 1",
        (estimate_id,),
    ).fetchone()
    conn.close()
    return row is not None


def count_estimates(search=""):
    conn = get_connection()
    query = (
        "SELECT COUNT(*) as cnt FROM estimates e "
        "LEFT JOIN clients c ON e.client_id = c.id WHERE 1=1"
        + _OPEN_ESTIMATE_SQL
    )
    params = []
    if search:
        query += " AND (c.name LIKE ? OR CAST(e.id AS TEXT) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row["cnt"]


def get_estimates(search="", limit=50, offset=0):
    conn = get_connection()
    query = """
        SELECT e.*, c.name as client_name
        FROM estimates e
        LEFT JOIN clients c ON e.client_id = c.id
        WHERE 1=1
    """ + _OPEN_ESTIMATE_SQL
    params = []

    if search:
        query += " AND (c.name LIKE ? OR CAST(e.id AS TEXT) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY e.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_estimate(estimate_id):
    conn = get_connection()
    row = conn.execute(
        """SELECT e.*, c.name as client_name, c.phone as client_phone,
                  c.email as client_email, c.address as client_address
           FROM estimates e
           LEFT JOIN clients c ON e.client_id = c.id
           WHERE e.id = ?""",
        (estimate_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    result["type"] = "Estimate"
    return result


def get_estimate_items(estimate_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM estimate_items WHERE estimate_id = ? ORDER BY id ASC",
        (estimate_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_estimate(
    client_id,
    total_amount,
    subtotal,
    tax_enabled,
    tax_rate,
    tax_amount,
    discount_type="flat",
    discount_percent=0,
    discount_amount=0,
    notes="",
    items=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO estimates
           (client_id, date, total_amount, subtotal, tax_enabled, tax_rate, tax_amount,
            discount_type, discount_percent, discount_amount, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            client_id,
            datetime.now().strftime("%Y-%m-%d"),
            total_amount,
            subtotal,
            1 if tax_enabled else 0,
            tax_rate if tax_enabled else 0,
            tax_amount if tax_enabled else 0,
            discount_type,
            discount_percent,
            discount_amount,
            notes,
        ),
    )
    estimate_id = cursor.lastrowid
    _insert_estimate_items(cursor, estimate_id, items or [])
    conn.commit()
    conn.close()
    return estimate_id


def update_estimate(
    estimate_id,
    client_id,
    total_amount,
    subtotal,
    tax_enabled,
    tax_rate,
    tax_amount,
    discount_type="flat",
    discount_percent=0,
    discount_amount=0,
    notes="",
    items=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE estimates SET
           client_id=?, total_amount=?, subtotal=?, tax_enabled=?, tax_rate=?, tax_amount=?,
           discount_type=?, discount_percent=?, discount_amount=?, notes=?
           WHERE id=?""",
        (
            client_id,
            total_amount,
            subtotal,
            1 if tax_enabled else 0,
            tax_rate if tax_enabled else 0,
            tax_amount if tax_enabled else 0,
            discount_type,
            discount_percent,
            discount_amount,
            notes,
            estimate_id,
        ),
    )
    if cursor.rowcount == 0:
        conn.close()
        return False

    cursor.execute("DELETE FROM estimate_items WHERE estimate_id = ?", (estimate_id,))
    _insert_estimate_items(cursor, estimate_id, items)
    conn.commit()
    conn.close()
    return True


def delete_estimate(estimate_id):
    conn = get_connection()
    conn.execute("DELETE FROM estimate_items WHERE estimate_id = ?", (estimate_id,))
    conn.execute("DELETE FROM estimates WHERE id = ?", (estimate_id,))
    conn.commit()
    conn.close()


# ── Invoices ──────────────────────────────────────────────────────────

def count_invoices(search=""):
    conn = get_connection()
    query = "SELECT COUNT(*) as cnt FROM invoices i LEFT JOIN clients c ON i.client_id = c.id WHERE 1=1"
    params = []
    if search:
        query += " AND (c.name LIKE ? OR CAST(i.id AS TEXT) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row["cnt"]


def get_invoices(search="", limit=50, offset=0):
    conn = get_connection()
    query = """
        SELECT i.*, c.name as client_name
        FROM invoices i
        LEFT JOIN clients c ON i.client_id = c.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (c.name LIKE ? OR CAST(i.id AS TEXT) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY i.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_invoice(invoice_id):
    conn = get_connection()
    row = conn.execute(
        """SELECT i.*, c.name as client_name, c.phone as client_phone,
                  c.email as client_email, c.address as client_address
           FROM invoices i
           LEFT JOIN clients c ON i.client_id = c.id
           WHERE i.id = ?""",
        (invoice_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    result["type"] = "Invoice"
    return result


def get_invoice_items(invoice_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY id ASC",
        (invoice_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_invoice(
    client_id,
    total_amount,
    subtotal,
    tax_enabled,
    tax_rate,
    tax_amount,
    discount_type="flat",
    discount_percent=0,
    discount_amount=0,
    status="Pending",
    notes="",
    items=None,
    source_estimate_id=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO invoices
           (client_id, date, total_amount, subtotal, tax_enabled, tax_rate, tax_amount,
            discount_type, discount_percent, discount_amount, status, source_estimate_id, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            client_id,
            datetime.now().strftime("%Y-%m-%d"),
            total_amount,
            subtotal,
            1 if tax_enabled else 0,
            tax_rate if tax_enabled else 0,
            tax_amount if tax_enabled else 0,
            discount_type,
            discount_percent,
            discount_amount,
            status,
            source_estimate_id,
            notes,
        ),
    )
    invoice_id = cursor.lastrowid
    _insert_invoice_items(cursor, invoice_id, items or [])
    conn.commit()
    conn.close()
    return invoice_id


def update_invoice_status(invoice_id, status):
    conn = get_connection()
    conn.execute("UPDATE invoices SET status = ? WHERE id = ?", (status, invoice_id))
    conn.commit()
    conn.close()


def convert_estimate_to_invoice(estimate_id):
    estimate = get_estimate(estimate_id)
    if not estimate:
        return None
    if estimate_is_converted(estimate_id):
        return None
    items = get_estimate_items(estimate_id)
    invoice_id = create_invoice(
        client_id=estimate["client_id"],
        total_amount=estimate["total_amount"],
        subtotal=estimate["subtotal"],
        tax_enabled=bool(estimate.get("tax_enabled")),
        tax_rate=estimate["tax_rate"],
        tax_amount=estimate["tax_amount"],
        discount_type=estimate.get("discount_type", "flat"),
        discount_percent=estimate["discount_percent"],
        discount_amount=estimate["discount_amount"],
        status="Pending",
        notes=estimate.get("notes", ""),
        items=items,
        source_estimate_id=estimate_id,
    )
    for item in items:
        if item["item_type"] == "product":
            decrement_stock(item["item_id"], item["quantity"])
    return invoice_id


def delete_invoice(invoice_id):
    conn = get_connection()
    items = conn.execute(
        "SELECT item_type, item_id, quantity FROM invoice_items WHERE invoice_id = ?",
        (invoice_id,),
    ).fetchall()
    for item in items:
        if item["item_type"] == "product":
            conn.execute(
                "UPDATE products SET stock_count = stock_count + ? WHERE id = ?",
                (item["quantity"], item["item_id"]),
            )
    conn.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    conn.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    conn.commit()
    conn.close()


# ── Maintenance Schedules ─────────────────────────────────────────────

def get_all_maintenance_schedules(search=""):
    conn = get_connection()
    query = """
        SELECT ms.*, c.name as client_name
        FROM maintenance_schedules ms
        JOIN clients c ON ms.client_id = c.id
    """
    params = []
    if search:
        query += " WHERE (c.name LIKE ? OR ms.service_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY CASE WHEN ms.status = 'Active' THEN 0 WHEN ms.status = 'Scheduled' THEN 1 ELSE 2 END, ms.next_due_date ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_maintenance_schedule(schedule_id):
    conn = get_connection()
    row = conn.execute(
        """SELECT ms.*, c.name as client_name
           FROM maintenance_schedules ms
           JOIN clients c ON ms.client_id = c.id
           WHERE ms.id = ?""",
        (schedule_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_maintenance_schedule(client_id, service_name, frequency, start_date, next_due_date, status, notes):
    conn = get_connection()
    conn.execute(
        """INSERT INTO maintenance_schedules
           (client_id, service_name, frequency, start_date, next_due_date, status, notes)
           VALUES (?,?,?,?,?,?,?)""",
        (client_id, service_name, frequency, start_date, next_due_date, status, notes),
    )
    conn.commit()
    conn.close()


def update_maintenance_schedule(schedule_id, client_id, service_name, frequency, start_date, next_due_date, status, notes):
    conn = get_connection()
    conn.execute(
        """UPDATE maintenance_schedules
           SET client_id=?, service_name=?, frequency=?, start_date=?, next_due_date=?,
               status=?, notes=?, updated_at=datetime('now')
           WHERE id=?""",
        (client_id, service_name, frequency, start_date, next_due_date, status, notes, schedule_id),
    )
    conn.commit()
    conn.close()


def mark_maintenance_completed(schedule_id):
    conn = get_connection()
    conn.execute(
        "UPDATE maintenance_schedules SET status='Completed', updated_at=datetime('now') WHERE id=?",
        (schedule_id,),
    )
    conn.commit()
    conn.close()


def delete_maintenance_schedule(schedule_id):
    conn = get_connection()
    conn.execute("DELETE FROM maintenance_schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()


# ── Dashboard Stats ───────────────────────────────────────────────────

def get_dashboard_stats(date_from, date_to):
    conn = get_connection()
    stats = {}

    row = conn.execute(
        """SELECT COALESCE(SUM(total_amount), 0) as total, COUNT(*) as cnt
           FROM invoices
           WHERE status='Paid' AND date >= ? AND date <= ?""",
        (date_from, date_to),
    ).fetchone()
    stats["sales_paid_total"] = row["total"]
    stats["sales_paid_count"] = row["cnt"]

    row = conn.execute(
        """SELECT COALESCE(SUM(total_amount), 0) as total, COUNT(*) as cnt
           FROM invoices
           WHERE status='Pending' AND date >= ? AND date <= ?""",
        (date_from, date_to),
    ).fetchone()
    stats["sales_pending_total"] = row["total"]
    stats["sales_pending_count"] = row["cnt"]

    row = conn.execute(
        """SELECT COALESCE(SUM(e.total_amount), 0) as total, COUNT(*) as cnt
           FROM estimates e
           WHERE e.date >= ? AND e.date <= ?"""
        + _OPEN_ESTIMATE_SQL,
        (date_from, date_to),
    ).fetchone()
    stats["estimates_total"] = row["total"]
    stats["estimates_count"] = row["cnt"]

    row = conn.execute(
        """SELECT COALESCE(SUM((ii.unit_price - ii.unit_cost) * ii.quantity), 0) as profit
           FROM invoice_items ii
           JOIN invoices i ON ii.invoice_id = i.id
           WHERE i.status='Paid' AND i.date >= ? AND i.date <= ?""",
        (date_from, date_to),
    ).fetchone()
    stats["profit_with_services"] = row["profit"]

    row = conn.execute(
        """SELECT COALESCE(SUM((ii.unit_price - ii.unit_cost) * ii.quantity), 0) as profit
           FROM invoice_items ii
           JOIN invoices i ON ii.invoice_id = i.id
           WHERE i.status='Paid' AND i.date >= ? AND i.date <= ?
             AND ii.item_type='product'""",
        (date_from, date_to),
    ).fetchone()
    stats["profit_products_only"] = row["profit"]

    low_stock = conn.execute(
        "SELECT * FROM products WHERE stock_count <= 5 ORDER BY stock_count ASC"
    ).fetchall()
    stats["low_stock"] = [dict(r) for r in low_stock]

    maintenance = conn.execute(
        """SELECT ms.*, c.name as client_name
           FROM maintenance_schedules ms
           JOIN clients c ON ms.client_id = c.id
           WHERE ms.status = 'Active'
           ORDER BY ms.next_due_date ASC"""
    ).fetchall()
    stats["maintenance_reminders"] = [dict(r) for r in maintenance]

    row = conn.execute(
        """SELECT COALESCE(SUM(discount_amount), 0) as total_discounts
           FROM invoices
           WHERE date >= ? AND date <= ?""",
        (date_from, date_to),
    ).fetchone()
    stats["total_discounts"] = row["total_discounts"]

    row = conn.execute("SELECT COUNT(*) as cnt FROM clients").fetchone()
    stats["total_clients"] = row["cnt"]

    conn.close()
    return stats
