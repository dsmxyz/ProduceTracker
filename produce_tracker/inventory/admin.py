from django.contrib import admin
from .models import Customer, Product, Inventory, Order, OrderItem

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Inventory)
admin.site.register(Order)
admin.site.register(OrderItem)