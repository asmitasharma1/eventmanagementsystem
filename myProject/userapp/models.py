from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('User', 'User'), ('Organizer', 'Organizer')])

    def __str__(self):
        return self.user.username
