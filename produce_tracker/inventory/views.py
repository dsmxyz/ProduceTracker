from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from .models import Customer, Inventory, Order, Product, OrderItem
from .forms import (LoginForm, CustomerForm, InventoryForm, InventorySearchForm, OrderForm, OrderItemForm, get_order_item_formset, ImportCSVForm)
from django.forms import inlineformset_factory
import csv
from io import TextIOWrapper
 

@login_required
def dashboard(request):
    # Calculate current stock
    culantro_small = Inventory.objects.filter(product__name='CS').aggregate(Sum('quantity'))['quantity__sum'] or 0
    culantro_large = Inventory.objects.filter(product__name='CL').aggregate(Sum('quantity'))['quantity__sum'] or 0
    thyme = Inventory.objects.filter(product__name='TH').aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Subtract ordered quantities
    ordered_cs = OrderItem.objects.filter(product__name='CS').aggregate(Sum('quantity'))['quantity__sum'] or 0
    ordered_cl = OrderItem.objects.filter(product__name='CL').aggregate(Sum('quantity'))['quantity__sum'] or 0
    ordered_th = OrderItem.objects.filter(product__name='TH').aggregate(Sum('quantity'))['quantity__sum'] or 0

    stock = {
        'culantro_small': culantro_small - ordered_cs,
        'culantro_large': culantro_large - ordered_cl,
        'thyme': thyme - ordered_th,
    }

    context = {
        'stock': stock,
        'recent_orders': Order.objects.order_by('-order_date')[:5],
        'recent_inventory': Inventory.objects.order_by('-arrival_date')[:5],
    }
    return render(request, 'inventory/dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# Customer CRUD views
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'inventory/customers/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer-list')
    else:
        form = CustomerForm()
    return render(request, 'inventory/customers/customer_form.html', {'form': form})

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer-list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'inventory/customers/customer_form.html', {'form': form})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer-list')  # Redirect to customer list after deletion

    return render(request, 'inventory/customers/customer_confirm_delete.html', {
        'customer': customer
    })

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'inventory/customers/customer_detail.html', {
        'customer': customer
    })

# Inventory CRUD views (similar pattern as customer views)
@login_required
def inventory_list(request):
    inventory_items = Inventory.objects.all().order_by('-arrival_date')
    search_form = InventorySearchForm(request.GET or None)

    if search_form.is_valid():
        product_type = search_form.cleaned_data.get('product_type')
        arrival_date = search_form.cleaned_data.get('arrival_date')

        if product_type:
            inventory_items = inventory_items.filter(product__name=product_type)
        if arrival_date:
            inventory_items = inventory_items.filter(arrival_date=arrival_date)

    # Calculate current stock
    stock = {
        'culantro_small': Inventory.objects.filter(product__name='CS').aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'culantro_large': Inventory.objects.filter(product__name='CL').aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'thyme': Inventory.objects.filter(product__name='TH').aggregate(Sum('quantity'))['quantity__sum'] or 0,
    }

    context = {
        'inventory_items': inventory_items,
        'search_form': search_form,
        'stock': stock,
    }
    return render(request, 'inventory/inventory/inventory_list.html', context)

@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item created successfully!')
            return redirect('inventory-list')
    else:
        form = InventoryForm()

    return render(request, 'inventory/inventory/inventory_form.html', {
        'form': form,
        'title': 'Add New Inventory Item',
        'products': Product.objects.all()
    })

@login_required
def inventory_update(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item updated successfully!')
            return redirect('inventory-list')
    else:
        form = InventoryForm(instance=inventory)

    return render(request, 'inventory/inventory/inventory_form.html', {
        'form': form,
        'title': f'Update {inventory.product.get_name_display()}'
    })

@login_required
def inventory_delete(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        inventory.delete()
        messages.success(request, 'Inventory item deleted successfully!')
        return redirect('inventory-list')

    return render(request, 'inventory/inventory/inventory_confirm_delete.html', {
        'inventory': inventory
    })

@login_required
def inventory_detail(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    return render(request, 'inventory/inventory/inventory_detail.html', {
        'inventory': inventory
    })

# Order CRUD views (similar pattern but with formset for order items)
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'inventory/orders/order_list.html', {'orders': orders})

@login_required
def order_create(request):
    OrderFormSet = inlineformset_factory(
        Order, 
        OrderItem, 
        form=OrderItemForm, 
        extra=1, 
        can_delete=True
    )

    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            return redirect('order-list')
    else:
        form = OrderForm()
        formset = OrderFormSet()

    return render(request, 'inventory/orders/order_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create New Order'
    })

@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)

    # Create the formset using the factory function
    OrderItemFormSet = get_order_item_formset()

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('order-detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(request, 'inventory/orders/order_form.html', {
        'form': form,
        'formset': formset,
        'order': order,
        'title': f'Edit Order #{order.pk}'
    })

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'inventory/orders/order_detail.html', {'order': order})

@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('order-list')

    return render(request, 'inventory/orders/order_confirm_delete.html', {'order': order})

@login_required
def packing_sheet(request, date=None):
    if date:
        orders = Order.objects.filter(delivery_date=date)
    else:
        orders = Order.objects.filter(is_delivered=False)

    products = Product.objects.all()
    packing_data = []

    for product in products:
        total = sum(item.quantity for order in orders for item in order.orderitem_set.filter(product=product))
        if total > 0:
            packing_data.append({
                'product': product,
                'quantity': total,
                'total_weight': total * product.weight,
            })

    context = {
        'orders': orders,
        'packing_data': packing_data,
        'total_weight': sum(item['total_weight'] for item in packing_data),
        'delivery_date': date,
    }
    return render(request, 'inventory/packing_sheet.html', context)

@login_required
def import_export(request):
    if request.method == 'POST':
        form = ImportCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding=request.encoding)
            reader = csv.DictReader(csv_file)
            model_choice = form.cleaned_data['model_choice']

            if model_choice == 'customer':
                for row in reader:
                    Customer.objects.create(
                        company_name=row['company_name'],
                        address=row['address'],
                        email=row['email'],
                        phone=row['phone'],
                        fax=row.get('fax', ''),
                    )
            # Similar handling for other models

            return redirect('import-export')
    else:
        form = ImportCSVForm()

    return render(request, 'inventory/import_export.html', {'form': form})

@login_required
def export_csv(request, model_name):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_name}_export.csv"'

    writer = csv.writer(response)

    if model_name == 'customers':
        writer.writerow(['company_name', 'address', 'email', 'phone', 'fax'])
        for customer in Customer.objects.all():
            writer.writerow([
                customer.company_name,
                customer.address,
                customer.email,
                customer.phone,
                customer.fax,
            ])
    # Similar for other models

    return response