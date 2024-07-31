from django.contrib.auth.models import BaseUserManager
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Prefetch
from .models import RideEvent


class CustomUserManager(BaseUserManager):
    def create_user(
        self, email, first_name, last_name, phone_number, role, password=None
    ):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role,
        )
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, first_name, last_name, phone_number, role, password=None
    ):
        """
        Create and return a superuser with an email, password, and appropriate privileges.
        """
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role,
            password=password,
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class RideManager(models.Manager):
    def today_ride_events(self):
        now = timezone.now()
        last_24_hours = now - timedelta(hours=24)
        today_events_queryset = RideEvent.objects.filter(created_at__gte=last_24_hours)

        return self.prefetch_related(
            Prefetch(
                "ride_events",
                queryset=today_events_queryset,
                to_attr="today_ride_events",
            )
        )
