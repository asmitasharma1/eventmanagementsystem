from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Event(models.Model):
    name=models.CharField(max_length=50)
    desc=models.CharField(max_length=50)
    img = models.ImageField(upload_to='myProject/pic/pic/')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    location = models.CharField(max_length=255, default='Unknown')
    ticket_template = models.ImageField(upload_to='myProject/pic/pic/', blank=True, null=True)
    number_of_tickets = models.PositiveIntegerField(null=True, blank=True)  # New field for tickets available
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field for ticket price
    organizer = models.ForeignKey(User, on_delete=models.CASCADE,default=1)  # Link to user who submits
    approved = models.BooleanField(default=False)  # Admin approval flag
    is_free = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)  # New field for latitude
    longitude = models.FloatField(null=True, blank=True)  # New field for longitude

    
    def clean(self):
        # Allow ticket price only if event is not free and ticket details are provided
        if not self.is_free:
            if self.ticket_price is not None and (self.number_of_tickets is None or self.ticket_template is None):
                raise ValidationError("Ticket price must be provided only if both number of tickets and ticket image are provided.")
        else:
            # If the event is free, ensure that ticket details are optional
            if self.ticket_price is not None or self.number_of_tickets is not None or self.ticket_template is not None:
                # If any ticket details are provided, it means it's not a free event
                raise ValidationError("This event is marked as free; ticket details should not be provided.")

    def __str__(self):
        return self.name


# Booking Model
class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    number_of_tickets = models.PositiveIntegerField(default=1)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Added field for ticket price
    booking_date = models.DateTimeField(auto_now_add=True)
    ticket_number = models.CharField(max_length=50, default="0000") 

    def save(self, *args, **kwargs):
        # If this is a new booking and the event has a ticket price, set it here
        if not self.pk and self.event and self.event.ticket_price is not None:
            self.ticket_price = self.event.ticket_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.event.name} by {self.name}" if self.event else f"Booking by {self.name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message