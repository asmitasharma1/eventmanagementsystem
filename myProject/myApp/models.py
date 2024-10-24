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
    organizer = models.ForeignKey(User, on_delete=models.CASCADE,default=1)  # Link to user who submits
    approved = models.BooleanField(default=False)  # Admin approval flag

    def __str__(self):
        return self.name

class Booking(models.Model):
    cus_name=models.CharField(max_length=55)
    cus_ph=models.CharField(max_length=12)
    name=models.ForeignKey(Event,on_delete=models.CASCADE)
    booking_date=models.DateField()
    booked_on=models.DateField(auto_now=True)