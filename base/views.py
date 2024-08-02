from rest_framework import viewsets
from .models import User, Ride, RideEvent
from .serializers import CustomUserSerializer, RideSerializer, RideEventSerializer
from .utils import paginator, calculate_and_sort_by_distance
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .permissions import AdminOnly
from django.db.models import Q


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.exclude(role="admin")
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
            openapi.Parameter(
                name="status",
                in_=openapi.IN_QUERY,
                description="Status of the Ride",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="email",
                in_=openapi.IN_QUERY,
                description="User Email",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="per_page",
                in_=openapi.IN_QUERY,
                description="Per Page for Pagination",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_filtered_queryset(request)
        paginated_data = self.get_paginated_data(queryset, request)
        paginated_data = self.sort_by_distance(paginated_data, request)
        return Response(paginated_data)

    def get_filtered_queryset(self, request):
        queryset = self.get_queryset()
        email = request.GET.get("email", "")
        status = request.GET.get("status", None)
        q_objects = Q(id_driver__email__icontains=email) | Q(
            id_rider__email__icontains=email
        )
        if status:
            q_objects &= Q(status=status)
        return queryset.filter(q_objects)

    def get_paginated_data(self, queryset, request):
        per_page = int(request.GET.get("per_page", 100))
        serializer = self.get_serializer
        return paginator(
            per_page=per_page,
            data=queryset,
            serializer=serializer,
            request=request,
        )

    def sort_by_distance(self, paginated_data, request):
        input_latitude = request.GET.get("latitude")
        input_longitude = request.GET.get("longitude")
        if not input_latitude or not input_longitude:
            return paginated_data

        try:
            latitude = float(input_latitude)
            longitude = float(input_longitude)
        except ValueError:
            # Handle invalid latitude/longitude here if needed
            return paginated_data

        return calculate_and_sort_by_distance(
            paginated_data=paginated_data,
            latitude=latitude,
            longitude=longitude,
        )
