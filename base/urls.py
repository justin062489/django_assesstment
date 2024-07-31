from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RideViewSet, RideEventViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="use")
router.register(r"rides", RideViewSet, basename="ride")
router.register(r"ride-events", RideEventViewSet, basename="ride-event")

urlpatterns = [
    path("", include(router.urls)),
]
