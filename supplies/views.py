"""
Django views for the supplies app.
Simple Django approach working directly with models.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import F, ExpressionWrapper, DecimalField
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from .models import Category, Supplier, Supply, StockMovement, PurchaseOrder, PurchaseOrderItem, get_dashboard_stats, CustomerRequest
from supplies.forms import (
    CategoryForm,
    SupplierForm,
    SupplyForm,
    StockMovementForm,
    StockAdjustmentForm,
    SearchForm,
    PurchaseOrderForm,
    PurchaseOrderItemForm,
    ReceiveItemForm,
    CustomerRequestForm,
    CustomerRequestItemForm,
    UnifiedRegistrationForm,
    CustomerRegistrationForm,
    ManagerRegistrationForm,  # <-- added
)
from .decorators import manager_required, customer_required


@manager_required
def dashboard(request):
    """Manager dashboard view with key metrics and recent activity."""
    stats = get_dashboard_stats()
    return render(request, 'supplies/dashboard.html', {'stats': stats})


@customer_required
def customer_dashboard(request):
    """Customer dashboard view showing available supplies and request status."""
    # Get available supplies for customers to browse
    available_supplies = Supply.objects.active().select_related('category', 'supplier').filter(current_stock__gt=0)[:10]
    
    # Get customer's recent requests
    recent_requests = CustomerRequest.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'available_supplies': available_supplies,
        'recent_requests': recent_requests,
        'total_requests': CustomerRequest.objects.filter(user=request.user).count(),
        'pending_requests': CustomerRequest.objects.filter(user=request.user, status='PENDING').count(),
    }
    return render(request, 'supplies/customer_portal/customer_dashboard.html', context)


def unified_dashboard(request):
    """Route users to appropriate dashboard based on their role."""
    if not request.user.is_authenticated:
        # Show landing page with login choices
        return render(request, 'home.html')
    
    # Superusers go to manager dashboard by default
    if request.user.is_superuser:
        return redirect('manager_dashboard')
    
    if hasattr(request.user, 'profile'):
        if request.user.profile.is_manager:
            return redirect('manager_dashboard')
        else:
            return redirect('customer_dashboard')
    else:
        # Create profile if it doesn't exist (fallback safety)
        from supplies.models import UserProfile
        UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'CUSTOMER'})
        return redirect('customer_dashboard')


# Category Views
@manager_required
def category_list(request):
    """List all categories."""
    categories = Category.objects.all()
    return render(request, 'supplies/categories/list.html', {'categories': categories})


@manager_required
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


@manager_required
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


@manager_required
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
@manager_required
def supplier_list(request):
    """List all suppliers."""
    suppliers = Supplier.objects.all()
    return render(request, 'supplies/suppliers/list.html', {'suppliers': suppliers})


@manager_required
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


@manager_required
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


@manager_required
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
@login_required
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


@manager_required
def supply_detail(request, supply_id):
    """View supply details and stock movements."""
    supply = get_object_or_404(Supply, id=supply_id)
    movements = StockMovement.objects.for_supply(supply_id, limit=20)
    
    return render(request, 'supplies/supplies/detail.html', {
        'supply': supply,
        'movements': movements
    })


@manager_required
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


@manager_required
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


@manager_required
def low_stock_report(request):
    """Show supplies with low stock."""
    low_stock_supplies = (
        Supply.objects
        .low_stock()
        .select_related('category', 'supplier')
        .annotate(
            annotated_total_value=ExpressionWrapper(
                F('current_stock') * F('unit_price'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
    )
    return render(request, 'supplies/reports/low_stock.html', {
        'supplies': low_stock_supplies
    })


# Purchase Order Views
@manager_required
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


@manager_required
def purchase_order_detail(request, order_id):
    """View purchase order details."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    return render(request, 'supplies/purchase_orders/detail.html', {'order': order})


@manager_required
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


@manager_required
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


@manager_required
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


@manager_required
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


@manager_required
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


@manager_required
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


@manager_required
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


@manager_required
def purchase_order_cancel(request, order_id):
    """Cancel a purchase order."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if request.method == 'POST':
        if order.can_be_cancelled():
            # Check original status before changing it
            original_status = order.status
            pending_items_count = order.get_pending_items_count() if original_status == 'PARTIALLY_RECEIVED' else 0
            
            order.status = 'CANCELLED'
            order.save()
            
            # Add reason for cancellation based on original status
            if original_status == 'PARTIALLY_RECEIVED':
                messages.success(request, f'Purchase Order {order.order_number} cancelled! {pending_items_count} remaining item(s) will not be delivered.')
            else:
                messages.success(request, f'Purchase Order {order.order_number} cancelled!')
        else:
            messages.error(request, 'Cannot cancel orders that have been fully received.')
    
    return redirect('purchase_order_detail', order_id=order_id)


@manager_required
def purchase_order_export_pdf(request, order_id):
    """Export a Purchase Order as PDF."""
    order = get_object_or_404(PurchaseOrder, id=order_id)
    html = render_to_string('supplies/purchase_orders/po_pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="PO-{order.order_number}.pdf"'
    result = pisa.CreatePDF(src=html, dest=response)
    if result.err:
        messages.error(request, 'Failed to generate PDF for this purchase order.')
        return redirect('purchase_order_detail', order_id=order_id)
    return response


# Authentication Views
def unified_register(request):
    """Unified registration for both managers and customers."""
    if request.method == 'POST':
        form = UnifiedRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            
            # Redirect based on role
            if user.profile.is_manager:
                return redirect('manager_dashboard')
            else:
                return redirect('customer_dashboard')
    else:
        form = UnifiedRegistrationForm()
    return render(request, 'supplies/customer_portal/register.html', {'form': form})


class UnifiedLoginView(LoginView):
    """Unified login for all users with role-based post-login redirect."""
    template_name = 'supplies/customer_portal/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.is_manager):
            return reverse_lazy('manager_dashboard')
        return reverse_lazy('customer_dashboard')


# Expose a function-compatible view for URL pattern expecting `views.unified_login`
unified_login = UnifiedLoginView.as_view()


class ManagerLoginView(LoginView):
    """Supply Manager login page."""
    template_name = 'supplies/manager_portal/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        # Managers and superusers go to manager dashboard
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.is_manager):
            return reverse_lazy('manager_dashboard')
        # Non-managers who used this page go to their dashboard
        return reverse_lazy('customer_dashboard')


class CustomerLoginView(LoginView):
    """Customer login page."""
    template_name = 'supplies/customer_portal/customer_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        # Customers go to customer dashboard
        if hasattr(user, 'profile') and user.profile.is_customer and not user.is_superuser:
            return reverse_lazy('customer_dashboard')
        # Managers/superusers who used this page go to manager dashboard
        return reverse_lazy('manager_dashboard')


def customer_register(request):
    """Customer-only registration page (sets profile.role = 'CUSTOMER')."""
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'supplies/customer_portal/customer_register.html', {'form': form})


def manager_register(request):
    """Manager-only registration page (sets profile.role = 'MANAGER')."""
    if request.method == 'POST':
        form = ManagerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Manager account created successfully!')
            return redirect('manager_dashboard')
    else:
        form = ManagerRegistrationForm()
    return render(request, 'supplies/manager_portal/manager_register.html', {'form': form})


def unified_logout(request):
    """Unified logout view with user feedback."""
    from django.contrib.auth import logout as auth_logout
    
    if request.user.is_authenticated:
        user_name = request.user.get_full_name() or request.user.username
        auth_logout(request)
        messages.success(request, f'Successfully signed out. See you later, {user_name}!')
    else:
        messages.info(request, 'You were already signed out.')
    
    return redirect('dashboard')


# Customer Request Views

@customer_required
def customer_my_requests(request):
    """Customer: list their own requests."""
    qs = CustomerRequest.objects.filter(user=request.user).prefetch_related('items', 'items__supply').order_by('-created_at')
    return render(request, 'supplies/customer_portal/my_requests.html', {
        'requests': qs
    })

@customer_required
def customer_request_detail_mine(request, request_id):
    """Customer: view a specific request they own (read-only)."""
    req = get_object_or_404(CustomerRequest, id=request_id, user=request.user)
    return render(request, 'supplies/customer_portal/request_detail.html', {
        'request_obj': req,
        'readonly': True,
    })

@customer_required
def customer_request_create(request):
    """Customer submits a stock request."""
    if request.method == 'POST':
        req_form = CustomerRequestForm(request.POST)
        item_form = CustomerRequestItemForm(request.POST)
        if req_form.is_valid() and item_form.is_valid():
            customer_request = req_form.save(commit=False)
            customer_request.status = 'PENDING'
            customer_request.created_by = 'Customer'
            customer_request.user = request.user
            # Set name/email/phone from user model
            customer_request.customer_name = request.user.get_full_name() or request.user.username
            customer_request.customer_email = request.user.email
            customer_request.customer_phone = getattr(request.user.profile, 'phone', '') if hasattr(request.user, 'profile') else ''
            customer_request.save()

            item = item_form.save(commit=False)
            item.request = customer_request
            item.save()

            messages.success(request, f"Request {customer_request.request_number} submitted! We will contact you soon.")
            return redirect('customer_my_requests')
    else:
        req_form = CustomerRequestForm()
        item_form = CustomerRequestItemForm()

    return render(request, 'supplies/customer_portal/request_create.html', {
        'req_form': req_form,
        'item_form': item_form,
    })


def customer_request_thanks(request, request_number):
    """Simple thank-you page."""
    cr = get_object_or_404(CustomerRequest, request_number=request_number)
    return render(request, 'supplies/customer_portal/request_detail.html', {
        'request_obj': cr,
        'readonly': True,
    })


@manager_required
def customer_request_list(request):
    """Manager page: list and filter customer requests."""
    status = request.GET.get('status', '')
    qs = CustomerRequest.objects.all().select_related()
    if status:
        qs = qs.filter(status=status)
    return render(request, 'supplies/customer_portal/request_list.html', {
        'requests': qs,
        'selected_status': status
    })


@manager_required
def customer_request_detail(request, request_id):
    """Manager page: view a single request."""
    req = get_object_or_404(CustomerRequest, id=request_id)
    return render(request, 'supplies/customer_portal/request_detail.html', {
        'request_obj': req,
        'readonly': False,
    })


@manager_required
def customer_request_approve(request, request_id):
    """Approve a customer request."""
    req = get_object_or_404(CustomerRequest, id=request_id)
    if request.method == 'POST':
        try:
            req.approve()
            messages.success(request, f"Request {req.request_number} approved.")
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('customer_request_detail', request_id=request_id)


@manager_required
def customer_request_out_for_delivery(request, request_id):
    """Mark request as out for delivery."""
    req = get_object_or_404(CustomerRequest, id=request_id)
    if request.method == 'POST':
        try:
            req.mark_out_for_delivery()
            messages.success(request, f"Request {req.request_number} marked as out for delivery.")
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('customer_request_detail', request_id=request_id)


@manager_required
def customer_request_delivered(request, request_id):
    """Mark request as delivered, deducting stock."""
    req = get_object_or_404(CustomerRequest, id=request_id)
    if request.method == 'POST':
        try:
            req.mark_delivered()
            messages.success(request, f"Request {req.request_number} delivered to customer. Stock updated.")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Delivery failed: {e}")
    return redirect('customer_request_detail', request_id=request_id)


@manager_required
def customer_request_cancel(request, request_id):
    """Cancel a request."""
    req = get_object_or_404(CustomerRequest, id=request_id)
    if request.method == 'POST':
        if req.status in ['PENDING', 'APPROVED']:
            req.status = 'CANCELLED'
            req.save(update_fields=['status'])
            messages.success(request, f"Request {req.request_number} cancelled.")
        else:
            messages.error(request, "Only pending or approved requests can be cancelled.")
    return redirect('customer_request_detail', request_id=request_id)


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


from django.shortcuts import render
from .models import StockMovement, StockAdjustment, PurchaseOrder
from django.contrib.auth.decorators import login_required

@login_required
def supply_transactions_report(request):
    """Show all supply transactions (stock movements and adjustments)."""
    stock_movements = StockMovement.objects.select_related('supply', 'user').order_by('-date')
    stock_adjustments = StockAdjustment.objects.select_related('supply', 'user').order_by('-date')
    return render(request, 'supplies/reports/supply_transactions.html', {
        'stock_movements': stock_movements,
        'stock_adjustments': stock_adjustments,
    })

@login_required
def po_status_report(request):
    """Show all PO transactions grouped by status."""
    purchase_orders = PurchaseOrder.objects.select_related('supplier').order_by('-order_date')
    return render(request, 'supplies/reports/po_status.html', {
        'purchase_orders': purchase_orders,
    })
