from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.owner_login, name='login'),
    path('logout/', views.owner_logout, name='logout'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('admin/login/', views.admin_login, name='admin_login'),
]
