# Supply Management System - Copilot Instructions

## Architecture Overview
Traditional Django MVC application with business logic encapsulated in models and custom managers. The project separates manager and customer workflows through role-based access control (UserProfile with MANAGER/CUSTOMER roles).

**Key Components:**
- **supplies app**: Single Django app handling all inventory, requests, and reporting
- **Dual-role system**: Managers handle inventory/POs; Customers request supplies
- **Models** [supplies/models.py]: Category, Supplier, Supply, StockMovement, PurchaseOrder, CustomerRequest, UserProfile
- **Views** [supplies/views.py]: 1120-line file with manager/customer views, form handling, PDF export
- **Templates**: Bootstrap-based UI in `/templates/supplies/` with dashboard, forms, and reports

## Role-Based Access Control
- **@manager_required decorator** [supplies/decorators.py]: Protects manager operations; superusers bypass
- **@customer_required decorator**: Restricts customer-only views (requests, my_requests)
- **UserProfile model**: Extended Django User with role/phone fields; auto-created via post_save signal
- **Dashboard routing**: `unified_dashboard()` routes authenticated users to manager/customer dashboard or home

## Business Logic Patterns

**Custom Managers** (business logic lives in managers, not views):
- `SupplyManager`: low_stock(), out_of_stock(), by_category(), search()
- `SupplierManager`: active(), with_supply_count()
- `CategoryManager`: with_supply_count()
- `StockMovementManager`: recent_movements(), supply_movements()

**Model Methods for State Changes:**
- `Supply.adjust_stock()`: Modifies stock + creates StockMovement record
- `Supply.stock_in() / stock_out()`: Wrapper methods using adjust_stock()
- `Supplier.deactivate()`: Sets is_active=False
- Use these instead of direct field updates to maintain audit trail

**Dashboard Stats:**
- Computed via `get_dashboard_stats()` helper function with aggregations (low_stock_count, total_suppliers, etc.)

## View Conventions

**URL Pattern Structure** [supplies/urls.py]:
- Manager routes: /categories/, /suppliers/, /supplies/, /purchase-orders/, /reports/
- Customer routes: /customer-dashboard/, /customer/requests/
- Shared: /manager/login/, /customer/login/ (separate login views)

**Form Submission Pattern:**
- GET = form page, POST = process + redirect to detail/list
- Successful POST redirects to detail view of created/updated object
- Use `messages.success(request, ...)` for user feedback

**QuerySet Optimization:**
- Use `.select_related()` for ForeignKey (supplier, category)
- Use `.prefetch_related()` for reverse relations (avoid N+1)
- Paginate large lists with `Paginator` (applied to supply/PO lists)

## Customer Request Workflow
CustomerRequest has status lifecycle: PENDING → APPROVED → OUT_FOR_DELIVERY → DELIVERED (or CANCELLED)

Workflow views:
- Customer creates request: `customer_request_create()` (CustomerRequestItemFormSet)
- Manager views requests: `customer_request_list()` (filtered by status)
- Manager transitions state: `customer_request_approve()`, `customer_request_out_for_delivery()`, etc.
- Each transition emits success message + redirects to detail

## Database Access
Django ORM only; no raw SQL. Utilize managers for filtered querysets:
```python
# Good: Uses manager
low_stock = Supply.objects.low_stock()

# Bad: Redundant filtering
Supply.objects.filter(current_stock__lte=F('minimum_stock'), is_active=True)
```

## External Dependencies
- **django-bootstrap5**: Used in templates for responsive UI
- **xhtml2pdf**: Generates PO PDFs (templates in `/templates/supplies/reports/pdf/`)
- **Pillow**: Image handling for supply photos

## Development Commands
- Migrations: `python manage.py migrate`
- Django check: `python manage.py check`
- Run server: `python manage.py runserver`
- Custom commands in `supplies/management/commands/`: create_admin.py, create_user_profiles.py, make_manager.py

## Common Extension Points
- **Add new supply attribute**: Add field to Supply model → makemigrations → migration
- **Add manager query**: Define in SupplyManager/SupplierManager → use in views
- **Add report**: Create view + template (follow existing report pattern in views)
- **Add customer workflow state**: Add choice to CustomerRequest.status, add transition view
