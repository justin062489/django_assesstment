from rest_framework import serializers
from .models import User, Ride, RideEvent


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "role",
        ]
        read_only_fields = ("is_active", "is_staff")
        extra_kwargs = {"password": {"write_only": True}, "role": {"write_only": True}}


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = "__all__"


class RideSerializer(serializers.ModelSerializer):
    today_ride_events = RideEventSerializer(many=True, read_only=True)

    class Meta:
        model = Ride
        fields = "__all__"
