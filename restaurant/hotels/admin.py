from django.contrib import admin
from .models import Restaurant, Table, MenuItem


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    # 🔹 EXISTING (kept)
    list_display = (
        'id',
        'name',
        'restaurant_type',
        'location',
        'rating',
        'status',        # ✅ added
        'owner'          # ✅ added
    )
    search_fields = ('name', 'location', 'owner__username')
    list_filter = ('restaurant_type', 'status')  # ✅ status added

    # 🔹 ADMIN ACTIONS (NEW)
    actions = ['approve_restaurants', 'reject_restaurants']

    def approve_restaurants(self, request, queryset):
        queryset.update(status='APPROVED')
    approve_restaurants.short_description = "Approve selected restaurants"

    def reject_restaurants(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_restaurants.short_description = "Reject selected restaurants"


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    # 🔹 EXISTING (unchanged)
    list_display = ('id', 'restaurant', 'table_number', 'seats', 'is_available')
    list_filter = ('restaurant', 'is_available')
    search_fields = ('restaurant__name', 'table_number')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    # 🔹 EXISTING (unchanged)
    list_display = ('id', 'restaurant', 'name', 'price')
    search_fields = ('name',)
    list_filter = ('restaurant',)
