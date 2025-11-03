"""
URL patterns for the supplies app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.unified_dashboard, name='dashboard'),
    path('manager-dashboard/', views.dashboard, name='manager_dashboard'),

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

    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/deactivate/', views.supplier_deactivate, name='supplier_deactivate'),

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
    path('api/supplies/search/', views.supply_search_api, name='supply_search_api'),

    # Authentication - separate login pages
    path('manager/login/', views.ManagerLoginView.as_view(), name='manager_login'),
    path('customer/login/', views.CustomerLoginView.as_view(), name='customer_login'),

    # Registration + unified auth kept for compatibility
    path('customer/register/', views.customer_register, name='customer_register'),
    path('manager/register/', views.manager_register, name='manager_register'),
    path('register/', views.unified_register, name='register'),
    path('login/', views.unified_login, name='login'),
    path('logout/', views.unified_logout, name='logout'),
]