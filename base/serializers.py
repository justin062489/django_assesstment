from rest_framework import serializers
from .models import User, Ride, RideEvent


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id_user",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "role",
        ]
        read_only_fields = ("is_active", "is_staff", "id_user")
        extra_kwargs = {
            "password": {"write_only": True},
        }


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = "__all__"


class RideSerializer(serializers.ModelSerializer):
    today_ride_events = RideEventSerializer(many=True, read_only=True)

    class Meta:
        model = Ride
        fields = "__all__"


class RideListSerializer(serializers.Serializer):
    id_ride = serializers.IntegerField()
    status = serializers.CharField()
    today_ride_events = RideEventSerializer(many=True, read_only=True)
    pickup_latitude = serializers.FloatField()
    pickup_longitude = serializers.FloatField()
    dropoff_latitude = serializers.FloatField()
    dropoff_longitude = serializers.FloatField()
    pickup_time = serializers.DateTimeField()
    # Writable fields for input
    id_rider_id = serializers.PrimaryKeyRelatedField(source="id_rider", read_only=True)
    id_driver_id = serializers.PrimaryKeyRelatedField(
        source="id_driver", read_only=True
    )
