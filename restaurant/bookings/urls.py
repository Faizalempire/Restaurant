from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path('list/', views.booking_list, name='booking_list'),
    path('cancel/<str:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('book/<int:hotel_id>/', views.book_table, name='book_table'),
    path('success/', views.booking_success, name='booking_success'),
]
