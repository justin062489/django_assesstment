from django.db import models

# Create your models here.
from django.db import models
from .choices import *
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from .managers import CustomUserManager


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    id_user = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    ## Added for Django Admin Purposes
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number", "role"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class Ride(models.Model):
    STATUS_CHOICES = [
        ("en-route", "En Route"),
        ("pickup", "Pickup"),
        ("dropoff", "Dropoff"),
    ]

    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    id_rider = models.ForeignKey(
        User,
        related_name="rider_rides",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    id_driver = models.ForeignKey(
        User,
        related_name="driver_rides",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    def __str__(self):
        return f"Ride {self.id_ride} - {self.status}"


class RideEvent(models.Model):
    id_ride_event = models.AutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride, on_delete=models.CASCADE, related_name="ride_events"
    )
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(editable=True)

    def __str__(self):
        return f"Event {self.id_ride_event} for Ride {self.id_ride.id_ride}"
