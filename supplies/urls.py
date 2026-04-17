"""
URL patterns for the supplies app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.unified_dashboard, name='dashboard'),
    path('manager-dashboard/', views.dashboard, name='manager_dashboard'),
    
    # Authentication
    # The unified login and register routes handle entry for all systems (Admin, Manager, Customer)
    path('register/', views.unified_register, name='register'),
    path('login/', views.unified_login, name='login'),
    path('logout/', views.unified_logout, name='logout'),

    # Admin Portal
    # These routes manage users, global settings, and view high-level logs.
    path('admin_portal/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_portal/users/', views.admin_user_management, name='admin_user_management'),
    path('admin_portal/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin_portal/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin_portal/users/<int:user_id>/deactivate/', views.admin_user_deactivate, name='admin_user_deactivate'),
    path('admin_portal/users/<int:user_id>/reset-password/', views.admin_user_reset_password, name='admin_user_reset_password'),
    path('admin_portal/inventory/', views.admin_inventory_overview, name='admin_inventory_overview'),
    path('admin_portal/purchase-orders/', views.admin_purchase_orders, name='admin_purchase_orders'),
    path('admin_portal/customer-requests/', views.admin_customer_requests, name='admin_customer_requests'),
    path('admin_portal/reports/', views.admin_comprehensive_report, name='admin_comprehensive_report'),
    path('admin_portal/reports/export/pdf/', views.admin_export_report_pdf, name='admin_export_report_pdf'),

    # Reports
    path('reports/stock-movements/', views.stock_movement_report, name='stock_movement_report'),
    path('reports/usage/', views.usage_report, name='usage_report'),
    path('reports/supplier-performance/', views.supplier_performance_report, name='supplier_performance_report'),
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),

    # Manager-facing Customer Requests (list, detail, actions)
    path('customer-requests/', views.customer_request_list, name='customer_request_list'),
    path('customer-requests/<int:request_id>/', views.customer_request_detail, name='customer_request_detail'),
    path('customer-requests/<int:request_id>/approve/', views.customer_request_approve, name='customer_request_approve'),
    path('customer-requests/<int:request_id>/out-for-delivery/', views.customer_request_out_for_delivery, name='customer_request_out_for_delivery'),
    path('customer-requests/<int:request_id>/delivered/', views.customer_request_delivered, name='customer_request_delivered'),
    path('customer-requests/<int:request_id>/cancel/', views.customer_request_cancel, name='customer_request_cancel'),

    # Customer portal (self-service)
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/requests/', views.customer_my_requests, name='customer_my_requests'),
    path('customer/requests/new/', views.customer_request_create, name='customer_request_create'),
    path('customer/requests/<int:request_id>/', views.customer_request_detail_mine, name='customer_request_detail_mine'),
    path('customer/requests/thanks/<str:request_number>/', views.customer_request_thanks, name='customer_request_thanks'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:category_id>/supplies/', views.category_supplies, name='category_supplies'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/deactivate/', views.supplier_deactivate, name='supplier_deactivate'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),

    # Supplies
    path('supplies/', views.supply_list, name='supply_list'),
    path('supplies/create/', views.supply_create, name='supply_create'),
    path('supplies/<int:supply_id>/', views.supply_detail, name='supply_detail'),
    path('supplies/<int:supply_id>/edit/', views.supply_edit, name='supply_edit'),
    path('supplies/<int:supply_id>/stock-movement/', views.stock_movement, name='stock_movement'),
    path('supplies/<int:supply_id>/stock-adjustment/', views.stock_adjustment, name='stock_adjustment'),

    # Purchase Orders
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:order_id>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:order_id>/edit/', views.purchase_order_edit, name='purchase_order_edit'),
    path('purchase-orders/<int:order_id>/add-item/', views.purchase_order_add_item, name='purchase_order_add_item'),
    path('purchase-orders/<int:order_id>/items/<int:item_id>/remove/', views.purchase_order_remove_item, name='purchase_order_remove_item'),
    path('purchase-orders/<int:order_id>/approve/', views.purchase_order_approve, name='purchase_order_approve'),
    path('purchase-orders/<int:order_id>/send/', views.purchase_order_send, name='purchase_order_send'),
    path('purchase-orders/<int:order_id>/items/<int:item_id>/receive/', views.purchase_order_receive_item, name='purchase_order_receive_item'),
    path('purchase-orders/<int:order_id>/cancel/', views.purchase_order_cancel, name='purchase_order_cancel'),
    path('purchase-orders/<int:order_id>/export/pdf/', views.purchase_order_export_pdf, name='purchase_order_export_pdf'),

    # Reports
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),

    # API
    # Endpoints intended for synchronous fetch calls from the frontend
    path('api/supplies/search/', views.supply_search_api, name='supply_search_api'),

    # Registration endpoints mapped directly to roles, keeping URLs separate for clarity
    path('customer/register/', views.customer_register, name='customer_register'),
    path('manager/register/', views.manager_register, name='manager_register'),
]