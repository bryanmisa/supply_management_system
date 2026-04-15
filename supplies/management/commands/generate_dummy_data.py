import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from faker import Faker
from supplies.models import (
    Category, Supplier, Supply, StockMovement,
    PurchaseOrder, PurchaseOrderItem,
    CustomerRequest, CustomerRequestItem, UserProfile
)

class Command(BaseCommand):
    help = 'Empties the database and generates related dummy data for a printer supplies business.'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        self.stdout.write(self.style.WARNING('Starting dummy data generation process...'))

        try:
            with transaction.atomic():
                # --- 1. Empty the database ---
                self.stdout.write('Clearing existing data...')
                StockMovement.objects.all().delete()
                CustomerRequestItem.objects.all().delete()
                CustomerRequest.objects.all().delete()
                PurchaseOrderItem.objects.all().delete()
                PurchaseOrder.objects.all().delete()
                Supply.objects.all().delete()
                Category.objects.all().delete()
                Supplier.objects.all().delete()
                User.objects.exclude(is_superuser=True).delete()
                
                # --- 2. Base Data (Categories, Suppliers, Users) ---
                self.stdout.write('Creating Categories...')
                categories_data = [
                    'Ink Cartridges', 'Toner Cartridges', 'Drum Units', 
                    'Printer Paper', 'Maintenance Kits', 'Printer Parts', 
                    '3D Printer Filaments', 'Labels & Ribbons'
                ]
                categories = []
                for cat_name in categories_data:
                    cat = Category.objects.create(name=cat_name, description=fake.text(100))
                    categories.append(cat)
                    
                self.stdout.write('Creating Suppliers...')
                suppliers = []
                for _ in range(15):
                    sup = Supplier.objects.create(
                        name=fake.company(),
                        contact_person=fake.name(),
                        email=fake.unique.email(),
                        phone=fake.phone_number()[:20],
                        address=fake.address(),
                        is_active=True
                    )
                    suppliers.append(sup)
                
                self.stdout.write('Creating Users...')
                users = []
                for _ in range(30):
                    # Create 5 Managers and 25 Customers
                    is_manager = _ < 5
                    u = User.objects.create_user(
                        username=fake.unique.user_name(),
                        email=fake.unique.email(),
                        password='password123',
                        first_name=fake.first_name()[:30],
                        last_name=fake.last_name()[:30],
                        is_staff=is_manager
                    )
                    target_role = 'MANAGER' if is_manager else 'CUSTOMER'
                    if not hasattr(u, 'profile'):
                        UserProfile.objects.create(user=u, role=target_role, phone=fake.phone_number()[:20])
                    else:
                        u.profile.role = target_role
                        u.profile.phone = fake.phone_number()[:20]
                        u.profile.save()
                    users.append(u)

                # --- 3. Supplies (100 Printer supplies) ---
                self.stdout.write('Creating 100 Printer Supplies...')
                brands = ['HP', 'Epson', 'Canon', 'Brother', 'Lexmark', 'Xerox', 'Kyocera']
                colors = ['Black', 'Cyan', 'Magenta', 'Yellow', 'Tri-color']
                types = ['Toner', 'Ink', 'Drum', 'Fuser', 'Developer']
                
                supplies = []
                for _ in range(100):
                    brand = random.choice(brands)
                    color = random.choice(colors)
                    stype = random.choice(types)
                    model_num = f"{random.randint(10, 999)}{random.choice(['A', 'X', 'XL', ''])}"
                    name = f"{brand} {model_num} {color} {stype}"
                    
                    if stype == 'Toner':
                        cat = categories[1]
                    elif stype == 'Ink':
                        cat = categories[0]
                    elif stype == 'Drum':
                        cat = categories[2]
                    else:
                        cat = categories[4]

                    # Give some randomized stock variance
                    stock_class = random.choices(
                        ['normal', 'low', 'out'], 
                        weights=[80, 15, 5], 
                        k=1
                    )[0]
                    minimum_stock = random.randint(10, 50)
                    
                    if stock_class == 'out':
                        initial_stock = 0
                    elif stock_class == 'low':
                        initial_stock = random.randint(1, minimum_stock)
                    else:
                        # Give huge enough padding for normal supplies to survive transactions
                        initial_stock = random.randint(minimum_stock + 10, 2000)
                    
                    supply = Supply.objects.create(
                        name=name[:200],
                        description=f"High quality {stype.lower()} cartridge for {brand} printers. Color: {color}",
                        sku=fake.unique.ean(length=13),
                        category=cat,
                        supplier=random.choice(suppliers),
                        current_stock=initial_stock, 
                        minimum_stock=minimum_stock,
                        maximum_stock=random.randint(2000, 5000),
                        unit_price=round(random.uniform(15.0, 300.0), 2),
                        unit_of_measure='pieces'
                    )
                    supplies.append(supply)

                # --- 4. Purchase Orders (30 data) ---
                self.stdout.write('Creating 30 Purchase Orders...')
                po_statuses = ['PENDING', 'APPROVED', 'SENT', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED']
                for _ in range(30):
                    po_status = random.choice(po_statuses)
                    po = PurchaseOrder.objects.create(
                        order_number=fake.unique.bothify(text='PO-########'),
                        supplier=random.choice(suppliers),
                        status=po_status,
                        notes=fake.sentence()
                    )
                    
                    # add items
                    num_items = random.randint(1, 5)
                    po_supplies = random.sample(supplies, num_items)
                    for sup in po_supplies:
                        ordered = random.randint(10, 100)
                        item = PurchaseOrderItem.objects.create(
                            purchase_order=po,
                            supply=sup,
                            quantity_ordered=ordered,
                            unit_price=sup.unit_price * round(random.uniform(0.8, 0.95), 2)
                        )
                        
                        if po_status == 'RECEIVED':
                            item.receive_quantity(ordered, reason=f'Received PO {po.order_number}')
                        elif po_status == 'PARTIALLY_RECEIVED':
                            received = random.randint(1, ordered - 1)
                            item.receive_quantity(received, reason=f'Partially received PO {po.order_number}')

                    po.calculate_total()
                    po.save()

                # --- 5. Customer Requests (70 data) ---
                self.stdout.write('Creating 70 Customer Requests...')
                cr_statuses = ['PENDING', 'APPROVED', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED']
                for _ in range(70):
                    u = random.choice(users)
                    status = random.choice(cr_statuses)
                    
                    cr = CustomerRequest.objects.create(
                        request_number=fake.unique.bothify(text='CR-##########'),
                        customer_name=u.get_full_name(),
                        customer_email=u.email,
                        customer_phone=u.profile.phone,
                        notes=fake.sentence(),
                        status='PENDING', # Start pending, then transition methods are called
                        user=u
                    )
                    
                    num_items = random.randint(1, 4)
                    cr_supplies = random.sample(supplies, num_items)
                    for sup in cr_supplies:
                        req_qty = random.randint(1, 5)
                        CustomerRequestItem.objects.create(
                            request=cr,
                            supply=sup,
                            quantity_requested=req_qty
                        )
                        
                    # Transition statuses
                    if status in ['APPROVED', 'OUT_FOR_DELIVERY', 'DELIVERED']:
                        cr.approve(approver='System')
                        if status in ['OUT_FOR_DELIVERY', 'DELIVERED']:
                            cr.mark_out_for_delivery()
                            if status == 'DELIVERED':
                                try:
                                    cr.mark_delivered()
                                except ValueError:
                                    cr.status = 'OUT_FOR_DELIVERY'
                                    cr.save()
                    elif status == 'CANCELLED':
                        cr.status = 'CANCELLED'
                        cr.save()

                # --- 6. Stock Movements (50 specific adjustments) ---
                self.stdout.write('Creating 50 Stock Adjustments...')
                # We do this after CR and PO so we explicitly add another 50 independent stock adjustments
                for _ in range(50):
                    sup = random.choice(supplies)
                    mov_type = random.choice(['IN', 'OUT', 'ADJUSTMENT', 'RETURN'])
                    qty = random.randint(1, 20)
                    reason = fake.sentence()[:190]
                    
                    try:
                        if mov_type == 'IN' or mov_type == 'RETURN':
                            sup.stock_in(qty, reference_number=fake.bothify(text='REF-####'), reason=reason)
                        else:
                            if sup.current_stock >= qty:
                                sup.stock_out(qty, reference_number=fake.bothify(text='REF-####'), reason=reason)
                            else:
                                sup.stock_in(qty, reason=reason)
                    except ValueError:
                        pass
                        
            self.stdout.write(self.style.SUCCESS(
                'Successfully cleared and recreated data: '
                '100 Printer Supplies, 30 Purchase Orders, 70 Customer Requests, and 50 standalone Stock Movements.'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating data: {e}'))
