from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'restaurant', 'table', 'date', 'time', 'status')
    list_filter = ('restaurant', 'status')
    search_fields = ('customer__username',)
