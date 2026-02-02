from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Supplier, Category, Supply


class SupplierDeleteTests(TestCase):
    def setUp(self):
        self.client = Client()
        # create manager user
        self.manager = User.objects.create_user(username='manager', password='pass')
        self.manager.profile.role = 'MANAGER'
        self.manager.profile.save()

        # create customer user
        self.customer = User.objects.create_user(username='customer', password='pass')
        # customer profile defaults to CUSTOMER

    def test_manager_can_delete_supplier_without_supplies(self):
        self.client.login(username='manager', password='pass')
        supplier = Supplier.objects.create(name='ToDelete')
        resp = self.client.post(reverse('supplier_delete', args=[supplier.id]))
        self.assertRedirects(resp, reverse('supplier_list'))
        self.assertFalse(Supplier.objects.filter(id=supplier.id).exists())

    def test_cannot_delete_supplier_with_supplies(self):
        self.client.login(username='manager', password='pass')
        supplier = Supplier.objects.create(name='HasSupplies')
        cat = Category.objects.create(name='C1')
        Supply.objects.create(name='S1', sku='SKU1', category=cat, supplier=supplier, unit_price=1.0)
        resp = self.client.post(reverse('supplier_delete', args=[supplier.id]))
        self.assertRedirects(resp, reverse('supplier_list'))
        self.assertTrue(Supplier.objects.filter(id=supplier.id).exists())

    def test_non_manager_cannot_delete_supplier(self):
        self.client.login(username='customer', password='pass')
        supplier = Supplier.objects.create(name='Nope')
        resp = self.client.post(reverse('supplier_delete', args=[supplier.id]))
        # manager_required should redirect or deny access; supplier must remain
        self.assertTrue(Supplier.objects.filter(id=supplier.id).exists())
