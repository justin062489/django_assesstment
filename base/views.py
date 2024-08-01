from rest_framework import viewsets
from .models import User, Ride, RideEvent
from .serializers import CustomUserSerializer, RideSerializer, RideEventSerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from .utils import paginator, calculate_and_sort_by_distance
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .permissions import AdminOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AdminOnly]


class RideViewSet(viewsets.ModelViewSet):
    serializer_class = RideSerializer
    permission_classes = [AdminOnly]

    def get_queryset(self):
        if self.action == "list":
            return Ride.objects.today_ride_events()
        else:
            return Ride.objects.all()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="latitude",
                in_=openapi.IN_QUERY,
                description="Latitude of the user's location",
                type=openapi.TYPE_NUMBER,
                format=openapi.FORMAT_DOUBLE,
                required=False,
            ),
            openapi.Parameter(
                name="longitude",
                in_=openapi.IN_QUERY,
                description="Longitude of the user's location",
                type=openapi.TYPE_NUMBER,
                format=openapi.FORMAT_DOUBLE,
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        input_latitude = request.GET.get("latitude", None)
        input_longtitude = request.GET.get("longitude", None)
        queryset = self.get_queryset()
        serializer = self.get_serializer
        per_page = 50
        ## Custom Paginator from utils
        paginated_data = paginator(
            per_page=per_page,
            data=queryset,
            serializer=serializer,
            request=request,
        )
        ## Sorting By GPS position(lat,lon)
        if input_latitude and input_longtitude:
            latitude = float(input_latitude)
            longitude = float(input_longtitude)
            paginated_data = calculate_and_sort_by_distance(
                paginated_data=paginated_data,
                latitude=latitude,
                longitude=longitude,
            )
        return Response(paginated_data)
