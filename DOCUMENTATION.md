# Supply Management System Verification & Architecture

This document serves as the high-level map of the Supply Management System. It replaces older disconnected `.md` files and provides a coherent view into the models, views, and system rules.

## 1. System Architecture

The project is built on Django, focusing on traditional Model-View-Template (MVT) flows.
- **Models** encode business rules natively via fat models (e.g. `adjust_stock` creates an audit log concurrently).
- **Views** heavily depend on standard forms. View functions enforce access roles via `@manager_required`, `@customer_required` or Django's built-in `login_required`.
- **Authentication** is handled via a unified single portal using a customized LoginView allowing different account roles to enter natively and resolve to their respective dashboards.

## 2. Access control and Roles 

The application utilizes an extended custom `UserProfile` (One-to-One with Django Default `User`).
There are three principal personas navigating the application:

### a) Customers
- Can browse available inventory across categories.
- Submit `CustomerRequest` for certain supply items.
- View their historical request records and current status via Customer Dashboards.

### b) Supply Managers (Managers)
- Administer and procure inventory (`Supply`).
- Handle `PurchaseOrders` from `Supplier`.
- Respond to and process `CustomerRequest` submissions (Approve $\rightarrow$ Out for Delivery $\rightarrow$ Delivered).
- View systemic data via Manager Dashboards (Inventory Valuation, Low Stock alerts, Stock movements).

### c) Administrators (Superusers)
- Django admin access for raw SQL modification.
- Dedicated `AdminPortal` with User CRUD and holistic export capabilities. Log in via the same portal but bypass most standard routes.

## 3. Core Models

* **Category & Supplier**: Simple categorical structures managing meta-data about items. Suppliers track business points-of-contact.
* **Supply**: The atomic inventory unit. Tracks `current_stock`, `minimum_stock`, `unit_price`, and relational constraints.
* **StockMovement**: The immutable audit ledger. Whenever `Supply.adjust_stock` is called (IN, OUT, ADJUSTMENT, RETURN), a `StockMovement` row is safely written.
* **PurchaseOrder & PurchaseOrderItem**: The inbound flow mechanics. Orders cycle through statuses to trigger `Supply.stock_in()` when items are "RECEIVED".
* **CustomerRequest & CustomerRequestItem**: The outbound flow mechanics. Similar to a cart, these cycle statuses and subtract inventory upon "DELIVERY".

## 4. Workflows

### Purchase Order Workflow
1. Manager creates `PurchaseOrder` with `Supplier`. 
2. Manager populates with `PurchaseOrderItem`s.
3. Upon approval and send, it's pending. When delivery occurs, manager clicks "Receive".
4. `item.receive_quantity()` is called. This automatically modifies `Supply` stock positively and emits a `StockMovement`. 

### Customer Request Workflow
1. Customer requests items.
2. Status stays `PENDING` until a Manager checks stock and "APPROVES".
3. Manager dispatches ("OUT_FOR_DELIVERY").
4. Manager marks "DELIVERED". Native logic (`mark_delivered()`) iterates all items and immediately decrements `Supply` amounts via `stock_out()`.

## 5. Development Details

The application attempts to isolate authentication flow (e.g. `/login/`) to provide an enterprise-looking monolithic entrance while mapping internally to diverse user realms, drastically shrinking UX fragmentation.

All views, models, forms, and core configuration logic are exhaustively commented inline for clarity when developing and debugging logic branches.
