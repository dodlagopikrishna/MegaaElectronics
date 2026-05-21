Role: You are a Security-Focused Software Architect.

Objective: Implement a robust Authentication and Role-Based Access Control (RBAC) system for the existing Python/SQLite retail application.

1. Database Schema Extensions:

Roles Table: id, role_name (e.g., Admin, Sales, Technician, Inventory).

Permissions Table: id, module_name (e.g., "Financials", "Stock_Edit", "Client_Delete").

Role_Permissions Table: Mapping roles to specific permissions.

Users Table: id, username, password_hash, role_id, is_active.

2. Authentication Logic:

Security: Use bcrypt or hashlib (with salt) for password storage. Never store plain text.

Login Screen: Create a modal/initial window that blocks access to the main app until successful authentication.

Session Management: Create a global CurrentUser singleton or class to store the logged-in user's ID, Name, and Permissions for the duration of the session.

3. Role Definitions & Task Mapping:

Admin (Super User): Full access to all modules, including User Management, Price Editing, and Profit Reports.

Sales Staff: Access to "Client Management," "Quotation Builder," and "Invoice Generation." They should not be able to see "Cost Prices" or "Delete" transactions.

Inventory Manager: Access to "Product Catalog" and "Stock Updates." No access to Financial Invoices or Sales reports.

Technician: Access only to the "Service/Maintenance Schedule" and the ability to mark services as "Complete."

4. UI/UX Requirements:

Dynamic Sidebar: The sidebar menu should only show buttons/tabs that the logged-in user has permission to access.

Action Guarding: Use Python decorators or conditional logic to "gray out" or hide specific buttons (like 'Delete' or 'Export Excel') based on the CurrentUser permissions.

5. Deliverables:

Provide the updated database_setup.py with the new tables and a default 'Admin' user creation script.

Provide a login_manager.py to handle password hashing and verification.

Provide a logic pattern for the GUI to check permissions before rendering a view.

6. First-Run & Default Admin Logic:

Bootstrap Function: Upon application startup, the software must check the Users table. If the table is empty, automatically create a default Admin account.

Default Credentials: >    * Username: admin

Password: admin123 (This must be stored as a hash, not plain text, even for the default).

Database Path: Ensure the script creates the SQLite .db file in the user's %APPDATA% folder if it doesn't already exist, then runs the table creation and Admin injection.