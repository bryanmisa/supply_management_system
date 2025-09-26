"""
Django admin configuration for supplies app.
"""
from django.contrib import admin
from .models import Category, Supplier, Supply, StockMovement, PurchaseOrder, PurchaseOrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'email']
    ordering = ['name']
    list_editable = ['is_active']


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'supplier', 'current_stock', 'minimum_stock', 'unit_price', 'is_active']
    list_filter = ['category', 'supplier', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    ordering = ['name']
    list_editable = ['current_stock', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'sku', 'is_active')
        }),
        ('Classification', {
            'fields': ('category', 'supplier')
        }),
        ('Stock Information', {
            'fields': ('current_stock', 'minimum_stock', 'maximum_stock', 'unit_of_measure')
        }),
        ('Pricing', {
            'fields': ('unit_price',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['supply', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'movement_date', 'created_by']
    list_filter = ['movement_type', 'movement_date', 'created_by']
    search_fields = ['supply__name', 'supply__sku', 'reason', 'reference_number']
    ordering = ['-movement_date']
    readonly_fields = ['movement_date']
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('supply', 'movement_type', 'quantity', 'previous_stock', 'new_stock')
        }),
        ('Details', {
            'fields': ('reason', 'reference_number', 'created_by')
        }),
        ('Timestamp', {
            'fields': ('movement_date',)
        }),
    )


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'status', 'order_date', 'total_amount', 'created_by']
    list_filter = ['status', 'order_date', 'supplier']
    search_fields = ['order_number', 'supplier__name', 'notes']
    ordering = ['-order_date']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'total_amount']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'supplier', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_delivery_date', 'actual_delivery_date')
        }),
        ('Details', {
            'fields': ('notes', 'total_amount', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'supply', 'quantity_ordered', 'quantity_received', 'unit_price', 'total_price']
    list_filter = ['purchase_order__status', 'created_at']
    search_fields = ['purchase_order__order_number', 'supply__name', 'supply__sku']
    ordering = ['-created_at']
