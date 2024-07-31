from rest_framework import viewsets
from .models import User, Ride, RideEvent
from .serializers import CustomUserSerializer, RideSerializer, RideEventSerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from .utils import paginator
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class RideViewSet(viewsets.ModelViewSet):
    serializer_class = RideSerializer

    def get_queryset(self):
        if self.action == "list":
            return Ride.objects.today_ride_events()
        else:
            return Ride.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer
        per_page = 50
        ## Custom Paginator from utils
        response_data = paginator(
            per_page=per_page,
            data=queryset,
            serializer=serializer,
            request=request,
        )
        return Response(response_data)


class RideEventViewSet(viewsets.ModelViewSet):
    queryset = RideEvent.objects.all()
    serializer_class = RideEventSerializer
