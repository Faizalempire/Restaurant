from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Restaurant(models.Model):
    # 🔹 Restaurant Owner (Staff user)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_restaurants"
    )

    # 🔹 Admin approval status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ],
        default='PENDING'
    )

    # 🔹 Restaurant details
    name = models.CharField(max_length=200)
    restaurant_type = models.CharField(
        max_length=50,
        choices=[('Veg', 'Veg'), ('Non-Veg', 'Non-Veg'), ('Both', 'Both')],
        default='Both'
    )
    location = models.CharField(max_length=200, blank=True, null=True)
    rating = models.FloatField(default=0)
    image = models.ImageField(upload_to='restaurant_images/', blank=True, null=True)

    def __str__(self):
        return self.name

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(r.rating for r in reviews)/reviews.count()
            self.rating=round(total_rating, 2)
        else:
            self.rating = 0
        self.save()       


class Table(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='tables'
    )
    table_number = models.IntegerField(blank=True, null=True)
    seats = models.IntegerField(default=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.table_number}"


class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

class Review(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.CharField(max_length=100, default="Anonymous")
    rating = models.IntegerField(default=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.restaurant.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed")
    ]

    PAYMENT_CHOICES = [
        ("OFFLINE", "Pay at Restaurant"),
        ("ONLINE", "Online Payment")
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="orders")
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="OFFLINE")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.restaurant.name} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


class TableBooking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="table_bookings"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="table_bookings")
    booking_date = models.DateField()
    booking_time = models.TimeField()
    guests = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant.name} | {self.user.username} | {self.booking_date}"
