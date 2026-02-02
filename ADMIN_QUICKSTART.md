# Administrator Portal - Quick Start Guide

## 🔐 How to Access Administrator Portal

### 1. **Access the Login Page**
   - Navigate to: `http://localhost:8000/`
   - Look for "Administrator" card
   - Click "Admin Sign in" button
   - URL: `/admin/login/`

### 2. **Login Requirements**
   - Must be a **superuser** account
   - Regular manager/customer accounts will be rejected
   - Contact system administrator for superuser access

### 3. **After Login**
   - Redirected to Administrator Dashboard
   - Access admin features from navigation sidebar or dashboard buttons

---

## 📍 Administrator Features Map

### Dashboard
**URL:** `/admin/dashboard/`
- System metrics overview
- Total users, supplies, suppliers, categories
- Pending customer requests count
- Low stock items alert
- Recent stock movements list
- Quick action buttons

### User Management
**URL:** `/admin/users/`
- **View all users** with role breakdown
- **Search** by username, email, name
- **Filter** by role (Manager/Customer)
- **Edit** user details (name, email, role)
- **Deactivate** inactive user accounts
- **Status** - View active/inactive status

### Edit User
**URL:** `/admin/users/<user_id>/`
- Change first name, last name
- Update email address
- Change user role (Manager ↔ Customer)
- Toggle active/inactive status
- Save changes button

### Inventory Overview
**URL:** `/admin/inventory/`
- **View all supplies** with complete details
- **Search** by name, SKU, description
- **Filter by:**
  - Category (dropdown)
  - Stock status (Low/Out/Overstock)
- **Display columns:**
  - Name, SKU, Category, Supplier
  - Current stock, Min/Max levels
  - Unit price, Total value
  - Status badge

### Purchase Orders
**URL:** `/admin/purchase-orders/`
- **View all purchase orders** system-wide
- **Filter by:**
  - Status (Pending, Approved, Sent, Received, Cancelled)
  - Supplier
  - Date range (start date optional)
- **Display:**
  - Order number, supplier, items count
  - Total amount, status, order date
  - View details button

### Customer Requests
**URL:** `/admin/customer-requests/`
- **View all customer requests** with real-time stats
- **Statistics dashboard:**
  - Total, Pending, Approved, In Transit, Delivered, Cancelled
- **Filter by:**
  - Status
  - Customer
  - Search request number/customer email
- **Display:**
  - Request number, customer name/email
  - Items count, status badge
  - Creation date/time

### Comprehensive Reports
**URL:** `/admin/reports/`
- **Generate reports** for specific date range
- **Default:** Last 30 days
- **Includes:**
  - System summary (users, supplies, inventory value)
  - Purchase order statistics
  - Customer request statistics
  - Stock movements list
- **Export as PDF** button

### Admin Dashboard (from sidebar)
Quick access to all admin features from navigation menu

---

## 🎯 Common Tasks

### Task: Find a Specific User
1. Go to User Management (`/admin/users/`)
2. Enter username/email in search box
3. Click "Filter" button
4. Click pencil icon to edit

### Task: Check Low Stock Items
1. Go to Inventory Overview (`/admin/inventory/`)
2. Select "Low Stock" from Status dropdown
3. Click "Filter" button
4. View all low stock items

### Task: Monitor Purchase Orders
1. Go to Purchase Orders (`/admin/purchase-orders/`)
2. Use filters for status, supplier, date range
3. Click "View" to see details

### Task: Generate Monthly Report
1. Go to Comprehensive Reports (`/admin/reports/`)
2. Select start date (1st of month)
3. Select end date (last of month)
4. Click "Generate Report"
5. Click "Export PDF" to download

### Task: Manage Customer Requests
1. Go to Customer Requests (`/admin/customer-requests/`)
2. View real-time statistics dashboard
3. Filter by status or customer
4. Click eye icon to view request details

---

## 🔄 Navigation Flow

```
Home Page
├─ Administrator Card
│  └─ Admin Sign in → Admin Login
│     └─ Admin Dashboard
│        ├─ User Management
│        ├─ Inventory Overview
│        ├─ Purchase Orders
│        ├─ Customer Requests
│        └─ Comprehensive Reports
└─ (Also accessible via sidebar when logged in)
```

---

## 📊 Dashboard Quick Reference

| Metric | Location | Description |
|--------|----------|-------------|
| Total Users | Admin Dashboard | All registered users |
| Total Managers | Admin Dashboard | Users with Manager role |
| Total Customers | Admin Dashboard | Users with Customer role |
| Total Supplies | Admin Dashboard | Active supplies in inventory |
| Low Stock Items | Admin Dashboard | Items below minimum threshold |
| Pending Requests | Admin Dashboard | Customer requests awaiting action |
| Total Purchase Orders | Admin Dashboard | All POs in system |

---

## 🖱️ Quick Links from Dashboard

- **Manage Users** → User Management page
- **Inventory** → Inventory Overview page
- **Purchase Orders** → Purchase Orders page
- **Customer Requests** → Customer Requests page
- **Reports** → Comprehensive Reports page

---

## ⚙️ Settings & Configuration

### User Roles
- **Superuser** - Full system access (Administrator)
- **Manager** - Inventory & purchase order management
- **Customer** - Request submission & tracking

### Default Filters
- Inventory: All active supplies
- Purchase Orders: All statuses
- Customer Requests: All statuses
- Reports: Last 30 days

### Pagination
- Users: 20 per page
- Purchase Orders: 25 per page
- Customer Requests: 25 per page
- Supplies: 25 per page

---

## 🔍 Search & Filter Tips

### Inventory Search
- **Name:** Full or partial supply name
- **SKU:** Product SKU code
- **Description:** Product description text

### User Search
- **Username:** User login name
- **Email:** User email address
- **Name:** First or last name

### Customer Request Search
- **Request #:** Unique request number
- **Customer:** Customer email or name
- **Status:** Dropdown selection

---

## 📈 Report Features

### Available Report Metrics
- System summary (users, inventory)
- Inventory value calculation
- Purchase order trends
- Customer request lifecycle
- Stock movement history

### Export Options
- **PDF Download** - Professional report format
- **Date Filtering** - Custom date ranges
- **Detailed Statistics** - Comprehensive breakdowns

---

## 🆘 Troubleshooting

### Cannot Access Admin Login
- ✅ Ensure you're superuser (Django admin access)
- ✅ Clear browser cache and try again
- ✅ Check if session is expired

### Search/Filter Not Working
- ✅ Verify you clicked "Filter" button
- ✅ Check for typos in search terms
- ✅ Try clearing all filters and start fresh

### PDF Export Failed
- ✅ Check browser console for errors
- ✅ Verify PDF library installed (xhtml2pdf)
- ✅ Try exporting to different folder

---

**For detailed implementation information, see [ADMIN_IMPLEMENTATION.md](ADMIN_IMPLEMENTATION.md)**
