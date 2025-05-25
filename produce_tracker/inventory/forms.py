from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from .models import Customer, Inventory, Order, OrderItem, Product

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'airway_bill', 'quantity', 'arrival_date']
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
        }

class InventorySearchForm(forms.Form):
    PRODUCT_CHOICES = [
        ('', 'All Products'),
        ('CS', 'Culantro Small (2kg)'),
        ('CL', 'Culantro Large (4kg)'),
        ('TH', 'Thyme (1kg)'),
    ]

    product_type = forms.ChoiceField(
        choices=PRODUCT_CHOICES,
        required=False,
        label='Filter by Product'
    )
    arrival_date = forms.DateField(
        required=False,
        label='Filter by Arrival Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'delivery_date', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'delivery_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            })
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})
        }

# Define the formset factory function (not the formset itself)
def get_order_item_formset(extra=1, can_delete=True):
    return inlineformset_factory(
        Order,
        OrderItem,
        form=OrderItemForm,
        extra=extra,
        can_delete=can_delete
    )

class ImportCSVForm(forms.Form):
    csv_file = forms.FileField()
    model_choice = forms.ChoiceField(choices=[
        ('customer', 'Customers'),
        ('inventory', 'Inventory'),
        ('order', 'Orders'),
    ])

OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    fields=['product', 'quantity'],
    extra=1,
    can_delete=True
)