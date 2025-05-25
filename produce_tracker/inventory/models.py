from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Customer(models.Model):
    company_name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse('customer-detail', kwargs={'pk': self.pk})


class Product(models.Model):
    CULANTRO_SMALL = 'CS'
    CULANTRO_LARGE = 'CL'
    THYME = 'TH'

    PRODUCT_CHOICES = [
        (CULANTRO_SMALL, 'Culantro Small (2kg)'),
        (CULANTRO_LARGE, 'Culantro Large (4kg)'),
        (THYME, 'Thyme (1kg)'),
    ]

    name = models.CharField(max_length=2, choices=PRODUCT_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

    @property
    def weight(self):
        weights = {'CS': 2, 'CL': 4, 'TH': 1}
        return weights.get(self.name, 0)


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    airway_bill = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    arrival_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.airway_bill}"

    def get_absolute_url(self):
        return reverse('inventory-detail', kwargs={'pk': self.pk})

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    is_delivered = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"

    def get_absolute_url(self):
        return reverse('order-detail', kwargs={'pk': self.pk})

    @property
    def total_weight(self):
        return sum(item.quantity * item.product.weight for item in self.orderitem_set.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order} - {self.product} x {self.quantity}"

    @property
    def total_weight(self):
        return self.quantity * self.product.weight