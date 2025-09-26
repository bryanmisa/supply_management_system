# Supply Management System

A Django-based inventory management system built with traditional Django architecture.

## Features
- Supply inventory management
- Category and supplier management  
- Stock movement tracking
- Low stock alerts
- Dashboard with key metrics
- Responsive Bootstrap UI

## Architecture
- Traditional Django MVC pattern
- Business logic in model methods and custom managers
- Direct model-view interaction
- Django ORM for data access

## Installation
1. Install Python 3.8+
2. Create virtual environment: `python -m venv .venv`
3. Activate virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run server: `python manage.py runserver`

## Usage
- Access the application at http://localhost:8000
- Admin interface at http://localhost:8000/admin
- Start by creating categories and suppliers
- Add supplies with stock information
- Use stock movements to track inventory changes

## Project Structure
```
supply_management_system/
├── supplies/                    # Main Django app
│   ├── models.py               # Models with business logic
│   ├── views.py                # View functions
│   ├── forms.py                # Django forms
│   ├── urls.py                 # URL patterns
│   ├── admin.py                # Admin configuration
│   └── migrations/             # Database migrations
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   └── supplies/              # App-specific templates
├── static/                     # Static files (CSS, JS, images)
└── supply_management_system/   # Django settings
```

## Key Models
- **Category**: Organize supplies into categories
- **Supplier**: Manage supplier information
- **Supply**: Core inventory items with stock tracking
- **StockMovement**: Track all inventory changes

## Custom Model Managers
- **CategoryManager**: Categories with supply counts
- **SupplierManager**: Active suppliers, supplier counts
- **SupplyManager**: Active supplies, low stock, search, filtering
- **StockMovementManager**: Recent movements, supply-specific movements

## Model Methods
- **Supply.adjust_stock()**: Adjust stock levels with movement tracking
- **Supply.stock_in()**: Add inventory
- **Supply.stock_out()**: Remove inventory
- **Supplier.deactivate()**: Deactivate supplier