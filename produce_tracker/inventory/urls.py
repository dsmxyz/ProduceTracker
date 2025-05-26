from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer-list'),
    path('customers/new/', views.customer_create, name='customer-create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer-update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer-delete'),
    path('customers/<int:pk>/', views.customer_detail, name='customer-detail'),

    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory-list'),
    path('inventory/new/', views.inventory_create, name='inventory-create'),
    path('inventory/<int:pk>/edit/', views.inventory_update, name='inventory-update'),
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory-delete'),
    path('<int:pk>/', views.inventory_detail, name='inventory-detail'),

    # Order URLs
    path('orders/', views.order_list, name='order-list'),
    path('orders/new/', views.order_create, name='order-create'),
    path('orders/<int:pk>/edit/', views.order_update, name='order-update'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order-delete'),
    path('orders/<int:pk>/', views.order_detail, name='order-detail'),

    # Packing Sheet
    path('packing/', views.packing_sheet, name='packing-sheet'),
    path('packing/<str:date>/', views.packing_sheet, name='packing-sheet-date'),

    # Import/Export
    path('import-export/', views.import_export, name='import-export'),
    path('export/<str:model_name>/', views.export_csv, name='export-csv'),
]