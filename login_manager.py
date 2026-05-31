import bcrypt
from database_setup import get_connection

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
ADMIN_PASSWORD_SYNC_KEY = "default_admin_password_v1"


class CurrentUser:
    """Singleton that holds the authenticated user's session data."""

    _instance = None

    def __init__(self):
        self.user_id = None
        self.username = None
        self.full_name = None
        self.role_ids = []
        self.role_names = []
        self.permissions = set()
        self.is_authenticated = False

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def display_name(self):
        name = (self.full_name or "").strip()
        return name if name else self.username

    def login(self, user_row, permissions):
        self.user_id = user_row["id"]
        self.username = user_row["username"]
        self.full_name = user_row.get("full_name") or ""
        self.permissions = set(permissions)
        self.is_authenticated = True

        conn = get_connection()
        rows = conn.execute(
            """SELECT r.id, r.role_name FROM user_roles ur
               JOIN roles r ON ur.role_id = r.id
               WHERE ur.user_id = ?
               ORDER BY r.id""",
            (self.user_id,),
        ).fetchall()
        conn.close()

        self.role_ids = [r["id"] for r in rows]
        self.role_names = [r["role_name"] for r in rows]

    def logout(self):
        self.user_id = None
        self.username = None
        self.full_name = None
        self.role_ids = []
        self.role_names = []
        self.permissions = set()
        self.is_authenticated = False

    def has_permission(self, permission_name):
        return permission_name in self.permissions


def hash_password(plain_password):
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password, stored_hash):
    return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash.encode("utf-8"))


def authenticate(username, password):
    """Verify credentials and return (user_row, permissions_list) or (None, None)."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
    ).fetchone()

    if not user:
        conn.close()
        return None, None

    if not verify_password(password, user["password_hash"]):
        conn.close()
        return None, None

    perms = conn.execute(
        """SELECT DISTINCT p.module_name
           FROM user_roles ur
           JOIN role_permissions rp ON ur.role_id = rp.role_id
           JOIN permissions p ON rp.permission_id = p.id
           WHERE ur.user_id = ?""",
        (user["id"],),
    ).fetchall()
    conn.close()

    return dict(user), [row["module_name"] for row in perms]


def _ensure_app_metadata(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS app_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL DEFAULT '')"
    )


def bootstrap_admin():
    """Ensure the default admin account exists with documented credentials."""
    conn = get_connection()
    cursor = conn.cursor()
    _ensure_app_metadata(conn)

    cursor.execute("SELECT id FROM roles WHERE role_name = 'Admin'")
    admin_role = cursor.fetchone()
    if not admin_role:
        conn.close()
        return False

    admin_role_id = admin_role["id"]
    changed = False

    cursor.execute("SELECT value FROM app_metadata WHERE key = ?", (ADMIN_PASSWORD_SYNC_KEY,))
    if cursor.fetchone() is None:
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (DEFAULT_ADMIN_USERNAME,),
        )
        admin_user = cursor.fetchone()
        if admin_user and not verify_password(
            DEFAULT_ADMIN_PASSWORD, admin_user["password_hash"]
        ):
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hash_password(DEFAULT_ADMIN_PASSWORD), admin_user["id"]),
            )
            changed = True
        cursor.execute(
            "INSERT INTO app_metadata (key, value) VALUES (?, '1')",
            (ADMIN_PASSWORD_SYNC_KEY,),
        )
        changed = True

    cursor.execute("SELECT * FROM users WHERE username = ?", (DEFAULT_ADMIN_USERNAME,))
    admin_user = cursor.fetchone()

    if admin_user is None:
        default_hash = hash_password(DEFAULT_ADMIN_PASSWORD)
        cursor.execute(
            """INSERT INTO users (full_name, username, password_hash, role_id, is_active, must_change_password)
               VALUES (?, ?, ?, ?, 1, 0)""",
            ("Administrator", DEFAULT_ADMIN_USERNAME, default_hash, admin_role_id),
        )
        user_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)",
            (user_id, admin_role_id),
        )
        changed = True
    else:
        cursor.execute(
            "SELECT 1 FROM user_roles WHERE user_id = ? AND role_id = ?",
            (admin_user["id"], admin_role_id),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)",
                (admin_user["id"], admin_role_id),
            )
            changed = True

    if changed:
        conn.commit()
    conn.close()
    return changed


def is_default_admin(user_id):
    """Check if the given user is the bootstrapped default admin."""
    conn = get_connection()
    row = conn.execute(
        "SELECT username FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row is not None and row["username"] == DEFAULT_ADMIN_USERNAME


def get_all_users():
    conn = get_connection()
    users_rows = conn.execute(
        "SELECT id, full_name, username, phone, is_active, created_at FROM users ORDER BY username"
    ).fetchall()

    result = []
    for u in users_rows:
        roles = conn.execute(
            """SELECT r.id as role_id, r.role_name FROM user_roles ur
               JOIN roles r ON ur.role_id = r.id
               WHERE ur.user_id = ?
               ORDER BY r.id""",
            (u["id"],),
        ).fetchall()

        result.append({
            "id": u["id"],
            "full_name": u["full_name"] or "",
            "username": u["username"],
            "phone": u["phone"] or "",
            "is_active": u["is_active"],
            "created_at": u["created_at"],
            "role_ids": [r["role_id"] for r in roles],
            "role_names": [r["role_name"] for r in roles],
            "is_default_admin": u["username"] == DEFAULT_ADMIN_USERNAME,
        })

    conn.close()
    return result


def get_active_users_with_phone():
    """Return active users who have a phone number set, with role info."""
    conn = get_connection()
    users_rows = conn.execute(
        "SELECT id, full_name, username, phone FROM users WHERE is_active = 1 AND phone != '' ORDER BY full_name"
    ).fetchall()

    result = []
    for u in users_rows:
        roles = conn.execute(
            """SELECT r.role_name FROM user_roles ur
               JOIN roles r ON ur.role_id = r.id
               WHERE ur.user_id = ?
               ORDER BY r.id""",
            (u["id"],),
        ).fetchall()

        display = (u["full_name"] or "").strip() or u["username"]
        role_str = ", ".join(r["role_name"] for r in roles)
        result.append({
            "id": u["id"],
            "full_name": u["full_name"] or "",
            "username": u["username"],
            "phone": u["phone"],
            "display_name": display,
            "roles": role_str,
        })

    conn.close()
    return result


def get_all_roles():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM roles ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(full_name, username, password, role_ids, *, is_active=1, phone=""):
    conn = get_connection()
    cursor = conn.cursor()
    pw_hash = hash_password(password)
    primary_role = role_ids[0] if role_ids else 0
    cursor.execute(
        """INSERT INTO users (full_name, username, password_hash, phone, role_id, is_active, must_change_password)
           VALUES (?, ?, ?, ?, ?, ?, 0)""",
        (full_name, username, pw_hash, phone, primary_role, is_active),
    )
    user_id = cursor.lastrowid

    for rid in role_ids:
        cursor.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)",
            (user_id, rid),
        )

    conn.commit()
    conn.close()


def update_user(user_id, full_name, username, role_ids, is_active, phone=""):
    conn = get_connection()
    cursor = conn.cursor()

    if is_default_admin(user_id):
        cursor.execute(
            "UPDATE users SET full_name = ?, username = ?, phone = ?, is_active = ? WHERE id = ?",
            (full_name, username, phone, is_active, user_id),
        )
    else:
        primary_role = role_ids[0] if role_ids else 0
        cursor.execute(
            "UPDATE users SET full_name = ?, username = ?, phone = ?, role_id = ?, is_active = ? WHERE id = ?",
            (full_name, username, phone, primary_role, is_active, user_id),
        )
        cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
        for rid in role_ids:
            cursor.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)",
                (user_id, rid),
            )

    conn.commit()
    conn.close()


def reset_user_password(user_id, new_password):
    conn = get_connection()
    pw_hash = hash_password(new_password)
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (pw_hash, user_id),
    )
    conn.commit()
    conn.close()


def change_own_password(new_password):
    """Change password for the currently logged-in user only."""
    current = CurrentUser.get()
    if not current.is_authenticated or current.user_id is None:
        return False, "You must be logged in to change your password."

    if len(new_password) < 4:
        return False, "New password must be at least 4 characters."

    conn = get_connection()
    user = conn.execute(
        "SELECT id FROM users WHERE id = ? AND is_active = 1",
        (current.user_id,),
    ).fetchone()
    conn.close()

    if not user:
        return False, "Your account could not be found."

    reset_user_password(current.user_id, new_password)
    return True, None


def delete_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
