"""
Django views for the supplies app.
Simple Django approach working directly with models.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import F

from .models import Category, Supplier, Supply, StockMovement, PurchaseOrder, PurchaseOrderItem, get_dashboard_stats
from .forms import CategoryForm, SupplierForm, SupplyForm, StockMovementForm, StockAdjustmentForm, SearchForm, PurchaseOrderForm, PurchaseOrderItemForm, ReceiveItemForm


def dashboard(request):
    """Dashboard view with key metrics and recent activity."""
    stats = get_dashboard_stats()
    return render(request, 'supplies/dashboard.html', {'stats': stats})


# Category Views
def category_list(request):
    """List all categories."""
    categories = Category.objects.all()
    return render(request, 'supplies/categories/list.html', {'categories': categories})


def category_create(request):
    """Create a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'supplies/categories/form.html', {'form': form, 'title': 'Create Category'})


def category_edit(request, category_id):
    """Edit an existing category."""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'supplies/categories/form.html', {
        'form': form, 
        'title': 'Edit Category',
        'category': category
    })


def category_delete(request, category_id):
    """Delete a category."""
    if request.method == 'POST':
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            messages.success(request, 'Category deleted successfully!')
        except Category.DoesNotExist:
            messages.error(request, 'Category not found.')
        except Exception:
            messages.error(request, 'Cannot delete category. It may be in use.')
    return redirect('category_list')


# Supplier Views
def supplier_list(request):
    """List all suppliers."""
    suppliers = Supplier.objects.all()
    return render(request, 'supplies/suppliers/list.html', {'suppliers': suppliers})


def supplier_create(request):
    """Create a new supplier."""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    
    return render(request, 'supplies/suppliers/form.html', {'form': form, 'title': 'Create Supplier'})


def supplier_edit(request, supplier_id):
    """Edit an existing supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'supplies/suppliers/form.html', {
        'form': form, 
        'title': 'Edit Supplier',
        'supplier': supplier
    })


def supplier_deactivate(request, supplier_id):
    """Deactivate a supplier."""
    if request.method == 'POST':
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            supplier.deactivate()
            messages.success(request, 'Supplier deactivated successfully!')
        except Supplier.DoesNotExist:
            messages.error(request, 'Supplier not found.')
    return redirect('supplier_list')


# Supply Views
def supply_list(request):
    """List all supplies with search and filtering."""
    supplies = Supply.objects.active().select_related('category', 'supplier')
    search_form = SearchForm()
    
    # Handle search
    if request.GET.get('query'):
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            supplies = Supply.objects.search(search_form.cleaned_data['query']).select_related('category', 'supplier')
    
    # Handle category filter
    category_id = request.GET.get('category')
    if category_id:
        supplies = Supply.objects.by_category(int(category_id)).select_related('category', 'supplier')
    
    # Pagination
    paginator = Paginator(supplies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    return render(request, 'supplies/supplies/list.html', {
        'page_obj': page_obj,
        'search_form': search_form,
        'categories': categories,
        'selected_category': category_id
    })


def supply_detail(request, supply_id):
    """View supply details and stock movements."""
    supply = get_object_or_404(Supply, id=supply_id)
    movements = StockMovement.objects.for_supply(supply_id, limit=20)
    
    return render(request, 'supplies/supplies/detail.html', {
        'supply': supply,
        'movements': movements
    })


def supply_create(request):
    """Create a new supply."""
    if request.method == 'POST':
        form = SupplyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supply created successfully!')
            return redirect('supply_list')
    else:
        form = SupplyForm()
    
    return render(request, 'supplies/supplies/form.html', {'form': form, 'title': 'Create Supply'})


def supply_edit(request, supply_id):
    """Edit an existing supply."""
    supply = get_object_or_404(Supply, id=supply_id)
    
    if request.method == 'POST':
        form = SupplyForm(request.POST, instance=supply)
        if form.is_valid():
            # Don't allow direct stock changes through this form
            supply_data = form.cleaned_data.copy()
            supply_data.pop('current_stock', None)
            
            for field, value in supply_data.items():
                setattr(supply, field, value)
            supply.save()
            
            messages.success(request, 'Supply updated successfully!')
            return redirect('supply_detail', supply_id=supply_id)
    else:
        form = SupplyForm(instance=supply)
    
    return render(request, 'supplies/supplies/form.html', {
        'form': form, 
        'title': 'Edit Supply',
        'supply': supply
    })


def stock_movement(request, supply_id):
    """Handle stock movements."""
    supply = get_object_or_404(Supply, id=supply_id)
    
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            try:
                movement_type = form.cleaned_data['movement_type']
                quantity = form.cleaned_data['quantity']
                reason = form.cleaned_data['reason']
                reference = form.cleaned_data['reference_number']
                
                if movement_type == 'IN':
                    supply.stock_in(quantity, reference, reason)
                elif movement_type == 'OUT':
                    supply.stock_out(quantity, reference, reason)
                else:  # ADJUSTMENT or RETURN
                    if movement_type == 'OUT' or movement_type == 'RETURN':
                        new_stock = supply.current_stock - quantity
                    else:
                        new_stock = supply.current_stock + quantity
                    supply.adjust_stock(new_stock, movement_type, reason, reference)
                
                messages.success(request, f'Stock {movement_type.lower()} recorded successfully!')
                return redirect('supply_detail', supply_id=supply_id)
            
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = StockMovementForm()
    
    return render(request, 'supplies/supplies/stock_movement.html', {
        'form': form,
        'supply': supply
    })


def stock_adjustment(request, supply_id):
    """Direct stock adjustment."""
    supply = get_object_or_404(Supply, id=supply_id)
    
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            try:
                new_quantity = form.cleaned_data['new_quantity']
                reason = form.cleaned_data['reason']
                reference = form.cleaned_data['reference_number']
                
                supply.adjust_stock(new_quantity, 'ADJUSTMENT', reason, reference)
                messages.success(request, 'Stock adjusted successfully!')
                return redirect('supply_detail', supply_id=supply_id)
            
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = StockAdjustmentForm(initial={'new_quantity': supply.current_stock})
    
    return render(request, 'supplies/supplies/stock_adjustment.html', {
        'form': form,
        'supply': supply
    })


def low_stock_report(request):
    """Show supplies with low stock."""
    # Include total_value annotation for display in the report
    low_stock_supplies = (
        Supply.objects
        .low_stock()
        .select_related('category', 'supplier')
        .annotate(total_value=F('current_stock') * F('unit_price'))
    )
    return render(request, 'supplies/reports/low_stock.html', {
        'supplies': low_stock_supplies
    })


# Purchase Order Views
def purchase_order_list(request):
    """List all purchase orders."""
    orders = PurchaseOrder.objects.select_related('supplier').prefetch_related('items')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by supplier
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        orders = orders.filter(supplier_id=supplier_id)
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    suppliers = Supplier.objects.filter(is_active=True)
    
    return render(request, 'supplies/purchase_orders/list.html', {
        'page_obj': page_obj,
        'suppliers': suppliers,
        'selected_status': status,
        'selected_supplier': supplier_id,
        'status_choices': PurchaseOrder.STATUS_CHOICES
    })


def purchase_order_detail(request, order_id):
    """View purchase order details."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    return render(request, 'supplies/purchase_orders/detail.html', {'order': order})


def purchase_order_create(request):
    """Create a new purchase order."""
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f'Purchase Order {order.order_number} created successfully!')
            return redirect('purchase_order_detail', order_id=order.id)
    else:
        form = PurchaseOrderForm()
    
    return render(request, 'supplies/purchase_orders/form.html', {
        'form': form, 
        'title': 'Create Purchase Order'
    })


def purchase_order_edit(request, order_id):
    """Edit a purchase order."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if order.status not in ['PENDING', 'APPROVED']:
        messages.error(request, 'Cannot edit orders that have been sent or received.')
        return redirect('purchase_order_detail', order_id=order_id)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase Order updated successfully!')
            return redirect('purchase_order_detail', order_id=order_id)
    else:
        form = PurchaseOrderForm(instance=order)
    
    return render(request, 'supplies/purchase_orders/form.html', {
        'form': form, 
        'title': 'Edit Purchase Order',
        'order': order
    })


def purchase_order_add_item(request, order_id):
    """Add item to purchase order."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if order.status not in ['PENDING', 'APPROVED']:
        messages.error(request, 'Cannot add items to orders that have been sent or received.')
        return redirect('purchase_order_detail', order_id=order_id)
    
    if request.method == 'POST':
        form = PurchaseOrderItemForm(request.POST, supplier=order.supplier)
        if form.is_valid():
            item = form.save(commit=False)
            item.purchase_order = order
            item.save()
            
            # Recalculate order total
            order.calculate_total()
            
            messages.success(request, 'Item added to purchase order!')
            return redirect('purchase_order_detail', order_id=order_id)
    else:
        form = PurchaseOrderItemForm(supplier=order.supplier)
    
    return render(request, 'supplies/purchase_orders/add_item.html', {
        'form': form,
        'order': order
    })


def purchase_order_remove_item(request, order_id, item_id):
    """Remove item from purchase order."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    item = get_object_or_404(PurchaseOrderItem, id=item_id, purchase_order=order)
    
    if order.status not in ['PENDING', 'APPROVED']:
        messages.error(request, 'Cannot remove items from orders that have been sent or received.')
        return redirect('purchase_order_detail', order_id=order_id)
    
    if request.method == 'POST':
        item.delete()
        order.calculate_total()
        messages.success(request, 'Item removed from purchase order!')
    
    return redirect('purchase_order_detail', order_id=order_id)


def purchase_order_approve(request, order_id):
    """Approve a purchase order."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if request.method == 'POST':
        if order.status == 'PENDING':
            order.status = 'APPROVED'
            order.save()
            messages.success(request, f'Purchase Order {order.order_number} approved!')
        else:
            messages.error(request, 'Only pending orders can be approved.')
    
    return redirect('purchase_order_detail', order_id=order_id)


def purchase_order_send(request, order_id):
    """Mark purchase order as sent to supplier."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if request.method == 'POST':
        if order.status == 'APPROVED':
            order.status = 'SENT'
            order.save()
            messages.success(request, f'Purchase Order {order.order_number} marked as sent!')
        else:
            messages.error(request, 'Only approved orders can be sent.')
    
    return redirect('purchase_order_detail', order_id=order_id)


def purchase_order_receive_item(request, order_id, item_id):
    """Receive items from purchase order."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    item = get_object_or_404(PurchaseOrderItem, id=item_id, purchase_order=order)
    
    max_quantity = item.quantity_pending
    
    if max_quantity <= 0:
        messages.error(request, 'This item has already been fully received.')
        return redirect('purchase_order_detail', order_id=order_id)
    
    if request.method == 'POST':
        form = ReceiveItemForm(request.POST, max_quantity=max_quantity)
        if form.is_valid():
            try:
                quantity = form.cleaned_data['quantity_received']
                reason = form.cleaned_data['reason'] or f"Received from PO {order.order_number}"
                
                item.receive_quantity(quantity, reason)
                messages.success(request, f'Received {quantity} units of {item.supply.name}!')
                
                return redirect('purchase_order_detail', order_id=order_id)
            
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = ReceiveItemForm(max_quantity=max_quantity, initial={'quantity_received': max_quantity})
    
    return render(request, 'supplies/purchase_orders/receive_item.html', {
        'form': form,
        'order': order,
        'item': item
    })


def purchase_order_cancel(request, order_id):
    """Cancel a purchase order."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if request.method == 'POST':
        if order.status in ['PENDING', 'APPROVED', 'SENT']:
            order.status = 'CANCELLED'
            order.save()
            messages.success(request, f'Purchase Order {order.order_number} cancelled!')
        else:
            messages.error(request, 'Cannot cancel orders that have been received.')
    
    return redirect('purchase_order_detail', order_id=order_id)


# API Views for AJAX requests
def supply_search_api(request):
    """API endpoint for supply search."""
    query = request.GET.get('q', '')
    if query:
        supplies = Supply.objects.search(query)[:10]  # Limit to 10 results
        results = [
            {
                'id': supply.id,
                'name': supply.name,
                'sku': supply.sku,
                'current_stock': supply.current_stock,
                'stock_status': supply.stock_status
            }
            for supply in supplies
        ]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})
