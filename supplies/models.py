"""
Django models for the supplies app.
Traditional Django approach with business logic in models and managers.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Q, F, Count
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """User profile to extend Django's User model with role and additional fields."""
    ROLE_CHOICES = [
        ('MANAGER', 'Supply Manager'),
        ('CUSTOMER', 'Customer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_manager(self):
        return self.role == 'MANAGER'
    
    @property
    def is_customer(self):
        return self.role == 'CUSTOMER'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class CategoryManager(models.Manager):
    """Custom manager for Category model."""
    
    def with_supply_count(self):
        """Return categories with count of supplies."""
        return self.annotate(supply_count=Count('supplies'))


class Category(models.Model):
    """Supply category model."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def supply_count(self):
        """Get number of supplies in this category."""
        return self.supplies.count()


class SupplierManager(models.Manager):
    """Custom manager for Supplier model."""
    
    def active(self):
        """Return only active suppliers."""
        return self.filter(is_active=True)
    
    def with_supply_count(self):
        """Return suppliers with count of supplies."""
        return self.annotate(supply_count=Count('supplies'))


class Supplier(models.Model):
    """Supplier model."""
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SupplierManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def supply_count(self):
        """Get number of supplies from this supplier."""
        return self.supplies.count()
    
    def deactivate(self):
        """Deactivate this supplier."""
        self.is_active = False
        self.save()


class SupplyManager(models.Manager):
    """Custom manager for Supply model."""
    
    def active(self):
        """Return only active supplies."""
        return self.filter(is_active=True)
    
    def low_stock(self):
        """Return supplies with low stock."""
        return self.filter(current_stock__lte=F('minimum_stock'), is_active=True)
    
    def out_of_stock(self):
        """Return supplies that are out of stock."""
        return self.filter(current_stock=0, is_active=True)
    
    def by_category(self, category_id):
        """Return supplies in a specific category."""
        return self.filter(category_id=category_id, is_active=True)
    
    def search(self, query):
        """Search supplies by name, SKU, or description."""
        return self.filter(
            Q(name__icontains=query) | 
            Q(sku__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )
    
    def with_totals(self):
        """Return supplies with calculated total values."""
        return self.annotate(
            total_value=F('current_stock') * F('unit_price')
        )


class Supply(models.Model):
    """Supply model - the core business object."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='supplies')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='supplies')
    
    # Stock information
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    maximum_stock = models.PositiveIntegerField(default=1000, validators=[MinValueValidator(1)])
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit_of_measure = models.CharField(max_length=20, default='pieces')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SupplyManager()

    class Meta:
        verbose_name_plural = "Supplies"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def is_low_stock(self):
        """Check if supply is below minimum stock level."""
        return self.current_stock <= self.minimum_stock
    
    @property
    def stock_status(self):
        """Get stock status as string."""
        if self.current_stock == 0:
            return "Out of Stock"
        elif self.is_low_stock:
            return "Low Stock"
        elif self.current_stock >= self.maximum_stock:
            return "Overstock"
        else:
            return "In Stock"
    
    @property
    def total_value(self):
        """Calculate total value of current stock."""
        return self.current_stock * self.unit_price
    
    def adjust_stock(self, new_quantity, movement_type='ADJUSTMENT', reason='', reference_number='', created_by='System'):
        """Adjust stock and create movement record."""
        if new_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        previous_stock = self.current_stock
        quantity_change = new_quantity - previous_stock
        
        # Create stock movement record
        StockMovement.objects.create(
            supply=self,
            movement_type=movement_type,
            quantity=abs(quantity_change),
            previous_stock=previous_stock,
            new_stock=new_quantity,
            reason=reason,
            reference_number=reference_number,
            created_by=created_by
        )
        
        # Update supply stock
        self.current_stock = new_quantity
        self.save()
    
    def stock_in(self, quantity, reference_number='', reason='Stock In', created_by='System'):
        """Add stock to this supply."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        new_stock = self.current_stock + quantity
        self.adjust_stock(new_stock, 'IN', reason, reference_number, created_by)
    
    def stock_out(self, quantity, reference_number='', reason='Stock Out', created_by='System'):
        """Remove stock from this supply."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.current_stock < quantity:
            raise ValueError("Insufficient stock available")
        
        new_stock = self.current_stock - quantity
        self.adjust_stock(new_stock, 'OUT', reason, reference_number, created_by)


class StockMovementManager(models.Manager):
    """Custom manager for StockMovement model."""
    
    def recent(self, limit=50):
        """Get recent stock movements."""
        return self.select_related('supply').order_by('-movement_date')[:limit]
    
    def for_supply(self, supply_id, limit=None):
        """Get movements for a specific supply."""
        queryset = self.select_related('supply').filter(supply_id=supply_id)
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    def by_date_range(self, start_date, end_date):
        """Get movements within a date range."""
        return self.select_related('supply').filter(
            movement_date__range=[start_date, end_date]
        )


class StockMovement(models.Model):
    """Stock movement model for tracking supply changes."""
    MOVEMENT_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('RETURN', 'Return'),
    ]
    
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    
    # Movement details
    reason = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=50, blank=True, help_text="PO number, invoice number, etc.")
    
    # Timestamps
    movement_date = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, default='System')  # In a real app, this would be a User FK
    
    objects = StockMovementManager()
    
    class Meta:
        ordering = ['-movement_date']
        
    def __str__(self):
        return f"{self.supply.name} - {self.get_movement_type_display()} ({self.quantity})"


def get_dashboard_stats():
    """Get dashboard statistics."""
    all_supplies = Supply.objects.active()
    low_stock_supplies = Supply.objects.low_stock()
    recent_movements = StockMovement.objects.recent(10)
    
    total_value = sum(supply.total_value for supply in all_supplies)
    out_of_stock_count = Supply.objects.out_of_stock().count()
    
    return {
        'total_supplies': all_supplies.count(),
        'low_stock_count': low_stock_supplies.count(),
        'out_of_stock_count': out_of_stock_count,
        'total_inventory_value': total_value,
        'recent_movements': recent_movements,
        'low_stock_supplies': low_stock_supplies[:5]  # Top 5 low stock items
    }


class PurchaseOrderManager(models.Manager):
    """Custom manager for PurchaseOrder model."""
    
    def pending(self):
        """Return pending purchase orders."""
        return self.filter(status='PENDING')
    
    def approved(self):
        """Return approved purchase orders."""
        return self.filter(status='APPROVED')
    
    def received(self):
        """Return received purchase orders."""
        return self.filter(status='RECEIVED')
    
    def by_supplier(self, supplier_id):
        """Return orders for a specific supplier."""
        return self.filter(supplier_id=supplier_id)


class PurchaseOrder(models.Model):
    """Purchase Order model for tracking orders to suppliers."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('SENT', 'Sent to Supplier'),
        ('PARTIALLY_RECEIVED', 'Partially Received'),
        ('RECEIVED', 'Fully Received'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, help_text="Auto-generated order number")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    
    # Order details
    order_date = models.DateTimeField(default=timezone.now)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Status and notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, help_text="Additional notes or special instructions")
    
    # Financial info
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, default='System')  # In a real app, this would be a User FK
    
    objects = PurchaseOrderManager()
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"PO-{self.order_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            from datetime import datetime
            year = datetime.now().year
            count = PurchaseOrder.objects.filter(created_at__year=year).count() + 1
            self.order_number = f"{year}-{count:04d}"
        super().save(*args, **kwargs)
    
    def calculate_total(self):
        """Calculate total amount from order items."""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        self.save()
        return total
    
    def mark_as_received(self):
        """Mark order as fully received and update stock."""
        for item in self.items.all():
            if item.quantity_received < item.quantity_ordered:
                # Auto-receive remaining quantities
                remaining = item.quantity_ordered - item.quantity_received
                item.receive_quantity(remaining, f"Auto-received for PO {self.order_number}")
        
        self.status = 'RECEIVED'
        self.actual_delivery_date = timezone.now().date()
        self.save()
    
    def has_pending_items(self):
        """Check if there are items that haven't been fully received."""
        return self.items.filter(quantity_received__lt=F('quantity_ordered')).exists()
    
    def get_pending_items_count(self):
        """Get count of items with pending quantities."""
        return self.items.filter(quantity_received__lt=F('quantity_ordered')).count()
    
    def can_be_cancelled(self):
        """Check if the order can be cancelled."""
        return self.status in ['PENDING', 'APPROVED', 'SENT', 'PARTIALLY_RECEIVED']


class PurchaseOrderItem(models.Model):
    """Individual items in a purchase order."""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    supply = models.ForeignKey(Supply, on_delete=models.PROTECT)
    
    # Quantities
    quantity_ordered = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantity_received = models.PositiveIntegerField(default=0)
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['purchase_order', 'supply']
        
    def __str__(self):
        return f"{self.supply.name} - {self.quantity_ordered} units"
    
    @property
    def total_price(self):
        """Calculate total price for this item."""
        return self.quantity_ordered * self.unit_price
    
    @property
    def quantity_pending(self):
        """Calculate remaining quantity to receive."""
        return self.quantity_ordered - self.quantity_received
    
    @property
    def is_fully_received(self):
        """Check if item is fully received."""
        return self.quantity_received >= self.quantity_ordered
    
    def receive_quantity(self, quantity, reason="Purchase order delivery"):
        """Receive a quantity of this item and update supply stock."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.quantity_received + quantity > self.quantity_ordered:
            raise ValueError("Cannot receive more than ordered quantity")
        
        # Update supply stock
        reference = f"PO-{self.purchase_order.order_number}"
        self.supply.stock_in(quantity, reference, reason)
        
        # Update received quantity
        self.quantity_received += quantity
        self.save()
        
        # Check if order is fully received
        if self.purchase_order.items.filter(quantity_received__lt=F('quantity_ordered')).count() == 0:
            self.purchase_order.status = 'RECEIVED'
            self.purchase_order.actual_delivery_date = timezone.now().date()
            self.purchase_order.save()
        elif self.purchase_order.status == 'SENT':
            self.purchase_order.status = 'PARTIALLY_RECEIVED'
            self.purchase_order.save()

class CustomerRequestManager(models.Manager):
    """Manager for CustomerRequest."""
    def pending(self):
        return self.filter(status='PENDING')
    def approved(self):
        return self.filter(status='APPROVED')
    def out_for_delivery(self):
        return self.filter(status='OUT_FOR_DELIVERY')
    def delivered(self):
        return self.filter(status='DELIVERED')

class CustomerRequest(models.Model):
    """Customer stock request header."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    request_number = models.CharField(max_length=50, unique=True, help_text="Auto-generated request number")
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, default='Customer')
    # Link request to the authenticated customer account
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='customer_requests')

    objects = CustomerRequestManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"CR-{self.request_number} - {self.customer_name} ({self.get_status_display()})"

    @property
    def total_items(self):
        return sum(i.quantity_requested for i in self.items.all())

    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = timezone.now().strftime("CR%Y%m%d%H%M%S")
        super().save(*args, **kwargs)

    def approve(self, approver='Manager'):
        if self.status != 'PENDING':
            raise ValueError("Only pending requests can be approved.")
        self.status = 'APPROVED'
        self.updated_at = timezone.now()
        self.save(update_fields=['status', 'updated_at'])

    def mark_out_for_delivery(self):
        if self.status != 'APPROVED':
            raise ValueError("Only approved requests can be marked out for delivery.")
        self.status = 'OUT_FOR_DELIVERY'
        self.updated_at = timezone.now()
        self.save(update_fields=['status', 'updated_at'])

    def mark_delivered(self):
        if self.status != 'OUT_FOR_DELIVERY':
            raise ValueError("Only requests out for delivery can be marked delivered.")
        # Deduct stock for each requested item
        for item in self.items.select_related('supply').all():
            # Reference number uses request_number
            item.supply.stock_out(
                item.quantity_requested,
                reference_number=self.request_number,
                reason=f"Delivered to customer: {self.customer_name}",
                created_by='Customer Portal'
            )
        self.status = 'DELIVERED'
        self.updated_at = timezone.now()
        self.save(update_fields=['status', 'updated_at'])


class CustomerRequestItem(models.Model):
    """Line item for a customer stock request."""
    request = models.ForeignKey(CustomerRequest, on_delete=models.CASCADE, related_name='items')
    supply = models.ForeignKey(Supply, on_delete=models.PROTECT, related_name='customer_request_items')
    quantity_requested = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.supply.name} x {self.quantity_requested}"
