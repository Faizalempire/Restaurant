from django.db import models
from django.conf import settings
from hotels.models import Restaurant, Table

class Booking(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='bookings')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bookings', blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    table_size = models.IntegerField(default=2)
    status = models.CharField(max_length=20, choices=[('confirmed','Confirmed'),('cancelled','Cancelled')], default='confirmed')

    def __str__(self):
        return f"{self.customer.username} - {self.restaurant.name} ({self.date} {self.time})"
