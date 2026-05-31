# MEGAA Electronics — Retail Management System

Local-first desktop application for **MEGAA Electronics** (Nellore, India): inventory, clients, estimates (quotes), invoices, PDF export, and WhatsApp sharing. Built for CCTV, projectors, and installation/maintenance services.

## Role: You are a Senior Full-Stack Engineer specializing in Python, Desktop Applications, and Local Databases.
## Objective: Build a local desktop application for a retail store that sells hardware (CCTV, Projectors) and services (Installation, Maintenance). The app must manage inventory, create PDF estimates, and generate purchase invoices.

---

## Quick start

```bash
cd "/Users/1041818/Desktop/MEGAA Electronics"
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python main.py
```

- **Runtime**: NiceGUI in **native mode** (pywebview desktop window, not a browser tab).
- **Default URL**: `http://127.0.0.1:8765/login`
- **Default admin** (bootstrapped on first run): `admin` / `admin123` — change in production deployments.

---

## Tech stack

| Layer | Choice |
|--------|--------|
| Language | Python 3.12+ (3.x) |
| UI | [NiceGUI](https://nicegui.io) 2.x + Tailwind utility classes via `.classes()` |
| Desktop shell | pywebview (`ui.run(native=True)`) |
| Database | SQLite (`sqlite3`, no ORM) |
| PDF | fpdf2 + Pillow (logo preprocessing) |
| Auth | bcrypt password hashes, RBAC in SQLite |

**Dependencies**: see `requirements.txt`. On macOS, `pyobjc-framework-WebKit` is required for native WebKit.

---

## Architecture

```
main.py                 # App entry, routing, sidebar shell, static mounts
store_config.py         # Store branding, GSTIN, DB filename, storage secret
database_setup.py       # Schema, migrations, app-data paths, seed data
models.py               # Data-access layer (CRUD + transactions)
login_manager.py        # CurrentUser session, auth, user admin APIs
ui_theme.py             # Design tokens, layout helpers, global CSS
pdf_generator.py        # Branded Estimate/Invoice PDFs → exports/
whatsapp_share.py       # wa.me links + reveal PDF in Finder/Explorer
country_phone_codes.py  # E.164 dial codes for client phone UI
views/                  # One render_*() per screen (NiceGUI composition)
  transaction_builder.py  # Shared quote/invoice form + totals math
```

### Layering rules

1. **Views** (`views/*.py`) — UI only: NiceGUI widgets, local `state` dicts, permission gates via `CurrentUser.has_permission()`.
2. **Models** (`models.py`) — All SQL; return plain `dict` rows. Open/close a connection per function (existing pattern).
3. **Infrastructure** — `database_setup`, `login_manager`, `store_config` — do not embed business UI here.
4. **Shared UI** — Reuse `ui_theme` helpers (`card`, `labeled_input`, `split_panels`, `success_button`, etc.) before inventing new class strings.

Do **not** add an ORM or separate API server unless explicitly requested; the product is offline, single-user-desktop.

### Application shell (`main.py`)

- `@ui.page("/login")` — unauthenticated entry.
- `@ui.page("/")` — authenticated shell: sidebar + dynamic main pane.
- Views are swapped in-place with CSS enter/exit transitions (`VIEW_TRANSITION_MS` in `ui_theme`).
- Static files: `/assets` → `assets/`, `/exports` → `exports/` (PDF output).

### Legacy / unused

- `responsive_ui.py` — CustomTkinter helpers from an earlier stack. **Not used** by the NiceGUI app. Do not extend unless migrating back.

---

## Configuration

**Single source of truth**: `store_config.py`

- Store name, address, GSTIN, phone, tagline, logo filenames, DB filename, NiceGUI `storage_secret`.
- Rebrand or relocate data by editing this module, not scattered literals.

**Database location** (not in the repo):

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/MEGAA Electronics/megaa_electronics.db` |
| Windows | `%APPDATA%\MEGAA Electronics\megaa_electronics.db` |
| Linux | `~/.megaa_electronics/megaa_electronics.db` |

Migrations copy from legacy names (`mega_electronics.db`, older app-support folder names) and from a project-local DB if present. Backups are timestamped in the app-data directory before overwrite imports.

**PDF output**: `exports/` next to source (served at `/exports` for preview links).

---

## Data model

### Business tables

- `products` — hardware: `cost_price`, `retail_price`, `stock_count`, `unit` (pcs, meters, …)
- `services` — labour: `rate`, `rate_type` (Flat Fee / Hourly Rate), `service_type` (Installation / Maintenance)
- `clients` — name, phone (+91 default in UI), email, address
- `transactions` — header: `type` (`Estimate` | `Invoice`), `status` (`Pending` | `Paid`), tax/discount fields, `notes`
- `transaction_items` — line items; `item_type` `product` | `service`; optional `maintenance_schedule`

### Auth / RBAC

- `users`, `roles`, `permissions`, `role_permissions`, `user_roles` (multi-role; `users.role_id` kept for legacy)
- Permissions are **string module names** (e.g. `Quotes_Create`, `Cost_Prices`, `Export_PDF`). Seeded in `database_setup._seed_roles_and_permissions()`.
- **Navigation** maps to permissions in `main.NAV_PERMISSIONS`; **actions** inside views check granular permissions separately.

Default roles: Admin (all), Sales, Inventory, Technician — see seed map in `database_setup.py`.

### Key business rules

- **Estimates** can be edited (`update_transaction` only when `type='Estimate'`).
- **Convert estimate → invoice** (`convert_estimate_to_invoice`): sets type/status and **decrements product stock** per line item.
- **Walk-in**: `client_id` may be null; display name falls back to "Walk-in Customer" in PDFs.
- **Currency / locale**: Indian Rupees (`₹`), GST labels in UI, default country code `+91` (`country_phone_codes.DEFAULT_COUNTRY_CODE`).
- **Dashboard**: paid invoice sum, pending totals, low stock (≤5), maintenance rows from line items.

---

## Authentication

- `CurrentUser` is a process-wide singleton (not NiceGUI server storage). Set on login in `views/login.py`; cleared on logout.
- Passwords: bcrypt via `login_manager.hash_password` / `verify_password`.
- `bootstrap_admin()` ensures default admin exists and syncs documented password once (tracked in `app_metadata`).
- `is_default_admin()` protects the bootstrap account from role deletion edge cases in user management.
- Enforce permissions in **both** nav visibility (`main._allowed_views`) and per-button/feature checks in views.

---

## UI conventions

Authoritative style reference: `Prompts/UI Style Guidelines.txt` and implemented tokens in `ui_theme.py`.

| Rule | Practice |
|------|----------|
| Styling | Tailwind via `.classes()`; avoid `.style()` except dynamic one-offs |
| Layout | Desktop-first, `w-full`, breakpoints `md:` / `lg:` |
| Primary color | `#3b82f6`; success `#10b981`; page background `#f2f2f7` |
| Components | Glassy cards (`CARD`), pill buttons (`BTN_*`), outlined Quasar inputs |
| Lists | Master–detail split (`split_panels`), search in toolbar, `empty_state` when no rows |
| Feedback | `notify_success` / `notify_warning`; destructive actions via `confirm_dialog` |

New screens should match existing views (`clients.py`, `products.py`) — same panel refresh pattern: hold `state`, `clear()` list/detail slots, re-render.

---

## Feature modules (views)

| Module | Permission (nav) | Notes |
|--------|------------------|-------|
| `dashboard.py` | `Dashboard` | Stats, low stock, maintenance reminders |
| `products.py` | `Products_View` | Tabs: products + services; cost column needs `Cost_Prices` |
| `clients.py` | `Clients_View` | CRUD; WhatsApp share; country code on phone |
| `quotes.py` | `Quotes_View` | Estimates; builder in `transaction_builder`; PDF + WhatsApp |
| `invoices.py` | `Invoices_View` | Invoices; convert from estimate; stock on convert |
| `user_management.py` | `User_Management` | Users + role assignment |
| `change_password.py` | (sidebar menu) | Self-service password change |

**PDF**: `pdf_generator.generate_transaction_pdf` — requires `Export_PDF` in UI.

**WhatsApp**: `whatsapp_share` opens `wa.me` with pre-filled text; PDF path revealed in OS file manager for manual attach.

---

## Adding a feature (checklist)

1. **Permission** — Add to `permissions` seed list and relevant roles in `database_setup.py` (existing DBs: migration or manual SQL if needed).
2. **Data** — Functions in `models.py`; schema change in `initialize_database()` with a `_migrate_*` helper if altering existing DBs.
3. **UI** — `views/<module>.py` + wire `VIEW_RENDERERS` / `NAV_*` in `main.py` if top-level nav.
4. **Gate** — `CurrentUser.has_permission("Your_Permission")` on every mutating control.
5. **Theme** — Use `ui_theme` primitives; keep strings out of views when they belong in `store_config`.

---

## Testing & quality

- No automated test suite today. Manual smoke path: login → create client → quote → PDF → convert to invoice → verify stock.
- After schema changes, test against a **copy** of `megaa_electronics.db` in app data.
- Do not commit: `__pycache__/`, `exports/*.pdf`, local `.db` files, `.DS_Store`.
- `seed_sample_data()` only runs when `products` is empty — safe for dev, not for production data resets.

---

## Security notes (local desktop)

- App binds to `127.0.0.1`; intended for single-machine use.
- `STORE_STORAGE_SECRET` is a fixed local secret for NiceGUI session storage — fine for offline desktop, not for multi-tenant hosting.
- Default admin credentials are for **initial setup**; document password change for deployed machines.
- SQL: use parameterized queries (existing pattern); never interpolate user input into SQL strings.

---

## Prompts / product docs

- `Prompts/App Creation Prompt.txt` — original product spec (CustomTkinter era; stack since moved to NiceGUI).
- `Prompts/Authentication prompt.md` — RBAC design notes.
- `Prompts/UI Style Guidelines.txt` — Tailwind/NiceGUI rules (slightly older color tokens; `ui_theme.py` wins on conflicts).

---

## Common pitfalls

- Importing `responsive_ui` or CustomTkinter patterns into NiceGUI views.
- Storing the DB in the repo — production data lives under Application Support only.
- Forgetting permission checks on toolbar buttons while only hiding sidebar nav.
- Editing invoices as if they were estimates — `update_transaction` is estimate-only.
- Hardcoding store strings — use `store_config` and PDF generator constants.
- Running without macOS WebKit dep — native window fails; install `pyobjc-framework-WebKit` on Darwin.

---
