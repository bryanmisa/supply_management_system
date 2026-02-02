# Administrator Portal - Complete URL Reference

## 🌐 Base URL
```
http://localhost:8000
```

---

## 🔐 Authentication

### Admin Login
- **URL:** `/admin/login/`
- **Method:** GET/POST
- **Access:** Public (redirects if already logged in)
- **Description:** Superuser-only login page
- **Requires:** Superuser credentials

---

## 📊 Dashboard & Overview

### Admin Dashboard
- **URL:** `/admin/dashboard/`
- **Method:** GET
- **Access:** `@admin_required` (superuser only)
- **Description:** System-wide overview with key metrics
- **Display:** 
  - Total users, managers, customers
  - Supplies, suppliers, categories
  - Low stock items count
  - Pending customer requests
  - Recent stock movements (10)

---

## 👥 User Management

### User Management List
- **URL:** `/admin/users/`
- **Method:** GET, POST (search/filter)
- **Parameters:**
  - `search` - Search by username, email, name
  - `role` - Filter by role (MANAGER, CUSTOMER)
  - `page` - Pagination (default: 20 per page)
- **Access:** `@admin_required`
- **Description:** List all users with filtering and search
- **Actions:**
  - View user details
  - Deactivate user

### User Detail & Edit
- **URL:** `/admin/users/<user_id>/`
- **Method:** GET, POST
- **Parameters:**
  - `user_id` - Django User ID (integer)
- **Post Fields:**
  - `first_name` - First name
  - `last_name` - Last name
  - `email` - Email address
  - `role` - Role (MANAGER or CUSTOMER)
  - `is_active` - Active status (checkbox)
- **Access:** `@admin_required`
- **Description:** View and edit user profile
- **Redirect:** Returns to user list on save

### User Deactivate
- **URL:** `/admin/users/<user_id>/deactivate/`
- **Method:** POST
- **Parameters:**
  - `user_id` - Django User ID (integer)
- **Access:** `@admin_required`
- **Description:** Deactivate a user account
- **Restrictions:** Cannot deactivate superusers
- **Redirect:** Returns to user list
- **Confirmation:** JavaScript confirmation required

---

## 📦 Inventory Management

### Inventory Overview
- **URL:** `/admin/inventory/`
- **Method:** GET, POST (search/filter)
- **Parameters:**
  - `search` - Search by name, SKU, description
  - `category` - Filter by category ID
  - `status` - Filter by status:
    - `low` - Low stock items
    - `out` - Out of stock items
    - `overstock` - Overstock items
  - `page` - Pagination (default: 25 per page)
- **Access:** `@admin_required`
- **Description:** View all supplies with advanced filtering
- **Display:**
  - Supply name, SKU, category
  - Supplier, current stock
  - Min/max levels, unit price
  - Total value, status badge
- **Query Optimization:**
  - `.select_related()` for category, supplier
  - Annotated total_value field
  - Paginated results

---

## 🛒 Purchase Order Management

### Purchase Orders List
- **URL:** `/admin/purchase-orders/`
- **Method:** GET, POST (search/filter)
- **Parameters:**
  - `status` - Filter by PO status:
    - `PENDING` - Pending orders
    - `APPROVED` - Approved orders
    - `SENT` - Sent to suppliers
    - `RECEIVED` - Received orders
    - `CANCELLED` - Cancelled orders
  - `supplier` - Filter by supplier ID
  - `start_date` - Filter by date (YYYY-MM-DD)
  - `end_date` - Filter by date (YYYY-MM-DD)
  - `page` - Pagination (default: 25 per page)
- **Access:** `@admin_required`
- **Description:** View all purchase orders system-wide
- **Display:**
  - Order number, supplier name
  - Item count, total amount
  - Status badge, order date
- **Query Optimization:**
  - `.select_related()` for supplier
  - `.prefetch_related()` for items
  - Date range filtering
  - Paginated results
- **Links:**
  - Eye icon → purchase_order_detail

---

## 📋 Customer Request Management

### Customer Requests List
- **URL:** `/admin/customer-requests/`
- **Method:** GET, POST (search/filter)
- **Parameters:**
  - `search` - Search by request number, customer name, email
  - `status` - Filter by request status:
    - `PENDING` - Awaiting approval
    - `APPROVED` - Approved requests
    - `OUT_FOR_DELIVERY` - In transit
    - `DELIVERED` - Completed requests
    - `CANCELLED` - Cancelled requests
  - `customer` - Filter by customer user ID
  - `page` - Pagination (default: 25 per page)
- **Access:** `@admin_required`
- **Description:** Manage all customer requests
- **Display:**
  - Request number, customer name/email
  - Item count, status badge
  - Creation date/time
  - Statistics dashboard (6 metrics)
- **Query Optimization:**
  - `.select_related()` for user
  - `.prefetch_related()` for items
  - Real-time aggregated statistics
  - Paginated results
- **Statistics:**
  - Total requests
  - Pending count
  - Approved count
  - Out for delivery count
  - Delivered count
  - Cancelled count
- **Links:**
  - Eye icon → customer_request_detail

---

## 📈 Reporting

### Comprehensive Report
- **URL:** `/admin/reports/`
- **Method:** GET, POST (search/filter)
- **Parameters:**
  - `start_date` - Start date (YYYY-MM-DD, optional)
  - `end_date` - End date (YYYY-MM-DD, optional)
- **Default:** Last 30 days if dates not provided
- **Access:** `@admin_required`
- **Description:** Generate comprehensive system reports
- **Display:**
  - System summary statistics
  - Purchase order statistics
  - Customer request statistics
  - Stock movement history (100 latest)
  - Date range display
- **Export Option:**
  - PDF download button

### Report PDF Export
- **URL:** `/admin/reports/export/pdf/`
- **Method:** GET, POST
- **Access:** `@admin_required`
- **Description:** Export comprehensive report as PDF
- **Response Type:** PDF document (application/pdf)
- **Filename:** `system_report.pdf`
- **Content:**
  - System summary
  - Statistics summaries
  - Generation timestamp
- **Template:** `supplies/admin_portal/report_pdf.html`

---

## 🔄 Navigation Flow

```
Home (/)
├─ Admin Login Card (/admin/login/)
│  ├─ Success → Admin Dashboard (/admin/dashboard/)
│  │  ├─ Quick Action: Manage Users (/admin/users/)
│  │  ├─ Quick Action: Inventory (/admin/inventory/)
│  │  ├─ Quick Action: Purchase Orders (/admin/purchase-orders/)
│  │  └─ Quick Action: Reports (/admin/reports/)
│  └─ Sidebar Menu (when logged in)
│     ├─ Admin Dashboard (/admin/dashboard/)
│     ├─ User Management (/admin/users/)
│     ├─ Inventory (/admin/inventory/)
│     ├─ Purchase Orders (/admin/purchase-orders/)
│     ├─ Customer Requests (/admin/customer-requests/)
│     └─ Reports (/admin/reports/)
└─ Manager Login Card (/manager/login/)
└─ Customer Login Card (/customer/login/)
```

---

## 🔗 Cross-Links

### From Admin Views to Manager Views
- Purchase Order Detail: `/purchase-orders/<order_id>/` (external link)
- Customer Request Detail: `/customer-requests/<request_id>/` (external link)
- Supply Detail: `/supplies/<supply_id>/` (external link)

### From Admin Views to Other Admin Views
- User Edit: `/admin/users/<user_id>/`
- User Deactivate: `/admin/users/<user_id>/deactivate/`
- Report PDF Export: `/admin/reports/export/pdf/`

---

## 📊 Query Parameters Combinations

### Valid Filter Combinations

**Users:**
```
/admin/users/?search=john&role=MANAGER&page=2
```

**Inventory:**
```
/admin/inventory/?search=laptop&category=1&status=low&page=1
```

**Purchase Orders:**
```
/admin/purchase-orders/?status=PENDING&supplier=5&start_date=2026-01-01&page=2
```

**Customer Requests:**
```
/admin/customer-requests/?search=REQ&status=DELIVERED&customer=3&page=1
```

**Reports:**
```
/admin/reports/?start_date=2026-01-01&end_date=2026-01-31
```

---

## 🌍 Base Domain Variables

Replace with your environment:
```
Local Development:  http://localhost:8000
Staging:            https://staging.example.com
Production:         https://www.example.com
```

---

## 📱 Mobile Responsive URLs

All URLs are fully responsive and work on:
- Desktop browsers
- Tablets
- Mobile devices

Responsive design handled by Bootstrap 5 framework.

---

## ⚡ Performance Tips

### Pagination
- Default: 20-25 items per page
- Adjust with `?page=X` parameter
- Use search/filter to reduce dataset

### Search Optimization
- Search is case-insensitive
- Supports partial matching
- Searches multiple fields simultaneously

### Date Filtering
- Format: `YYYY-MM-DD`
- Converts to UTC internally
- Includes full day (00:00 - 23:59)

---

## 🔐 Access Control

**All Admin URLs require:**
- ✅ User must be authenticated
- ✅ User must be superuser
- ✅ Login at `/admin/login/`
- ✅ Regular users redirected appropriately

---

## 📋 Error Handling

### Common Errors

**404 Not Found:**
- Invalid user ID or resource not found
- Check URL parameters

**403 Forbidden:**
- Not authenticated
- Not superuser
- Redirect to login page

**400 Bad Request:**
- Invalid filter values
- Invalid date format
- Check parameter types

---

## 🔍 API-like Endpoints

Admin endpoints follow REST-like patterns:

```
GET     /admin/users/                    → List
POST    /admin/users/                    → Search/Filter
GET     /admin/users/<id>/               → Detail
POST    /admin/users/<id>/               → Update
POST    /admin/users/<id>/deactivate/    → Delete (deactivate)
```

---

## 📞 Support URLs

For detailed documentation, see:
- [ADMIN_IMPLEMENTATION.md](ADMIN_IMPLEMENTATION.md) - Full implementation details
- [ADMIN_QUICKSTART.md](ADMIN_QUICKSTART.md) - Quick reference guide
- [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) - Feature checklist

---

**Last Updated:** January 30, 2026
**Status:** Complete and Ready for Use ✅
