"""
Django forms for the supplies app.
"""
from django import forms
from django.core.exceptions import ValidationError
from supplies.models import Category, Supplier, Supply, PurchaseOrder, PurchaseOrderItem, CustomerRequest, CustomerRequestItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category description'})
        }


class SupplierForm(forms.ModelForm):
    """Form for creating and editing suppliers."""
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact person'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class SupplyForm(forms.ModelForm):
    """Form for creating and editing supplies."""
    
    class Meta:
        model = Supply
        fields = [
            'name', 'description', 'sku', 'category', 'supplier',
            'minimum_stock', 'maximum_stock', 'unit_price', 'unit_of_measure',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supply name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Supply description'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'maximum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., pieces, kg, liters'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)


class StockMovementForm(forms.Form):
    """Form for stock movements."""
    MOVEMENT_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('RETURN', 'Return'),
    ]
    
    movement_type = forms.ChoiceField(
        choices=MOVEMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
    reason = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason for movement'})
    )
    reference_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO number, invoice, etc.'})
    )


class StockAdjustmentForm(forms.Form):
    """Form for direct stock adjustments."""
    new_quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    reason = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason for adjustment'})
    )
    reference_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference number'})
    )


class SearchForm(forms.Form):
    """Form for searching supplies."""
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, SKU, or description...',
            'autofocus': True
        })
    )


class PurchaseOrderForm(forms.ModelForm):
    """Form for creating and editing purchase orders."""
    
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'expected_delivery_date', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special instructions or notes'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)


class PurchaseOrderItemForm(forms.ModelForm):
    """Form for adding items to purchase orders."""
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['supply', 'quantity_ordered', 'unit_price']
        widgets = {
            'supply': forms.Select(attrs={'class': 'form-select'}),
            'quantity_ordered': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
        }

    def __init__(self, *args, **kwargs):
        supplier = kwargs.pop('supplier', None)
        super().__init__(*args, **kwargs)
        
        if supplier:
            # Filter supplies by supplier
            self.fields['supply'].queryset = Supply.objects.filter(supplier=supplier, is_active=True)
        else:
            self.fields['supply'].queryset = Supply.objects.filter(is_active=True)


class ReceiveItemForm(forms.Form):
    """Form for receiving items from purchase orders."""
    quantity_received = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
    reason = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason for receiving'})
    )

    def __init__(self, *args, **kwargs):
        max_quantity = kwargs.pop('max_quantity', None)
        super().__init__(*args, **kwargs)
        
        if max_quantity:
            self.fields['quantity_received'].widget.attrs['max'] = max_quantity
            self.fields['quantity_received'].help_text = f"Maximum: {max_quantity}"


class CustomerRequestForm(forms.ModelForm):
    """Form for customers to request stock."""
    class Meta:
        model = CustomerRequest
        fields = ['customer_name', 'customer_email', 'customer_phone', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes (optional)'}),
        }

class CustomerRequestItemForm(forms.ModelForm):
    """Form for selecting supply and quantity (limited to available stock)."""
    class Meta:
        model = CustomerRequestItem
        fields = ['supply', 'quantity_requested']
        widgets = {
            'supply': forms.Select(attrs={'class': 'form-select'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def clean(self):
        cleaned = super().clean()
        supply = cleaned.get('supply')
        qty = cleaned.get('quantity_requested') or 0
        if supply and qty:
            if not supply.is_active:
                raise ValidationError("Selected supply is not active.")
            if qty > supply.current_stock:
                raise ValidationError(f"Requested quantity exceeds available stock ({supply.current_stock}).")
        return cleaned


class CustomerRegistrationForm(UserCreationForm):
    """Simple customer registration form."""
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }