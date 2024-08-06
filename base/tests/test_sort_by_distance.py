import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from base.models import Ride, User
from base.utils import calculate_and_sort_by_distance


@pytest.fixture
def create_admin():
    return User.objects.create_user(
        email="admin_test@admin.com",
        password="1234",
        first_name="Admin",
        last_name="User",
        role="admin",
        phone_number="321321321",
    )


@pytest.fixture
def create_driver():
    driver_default_kwargs = {
        "password": "password1234",
        "first_name": "drivertest_firstname",
        "last_name": "drivertest_lastname",
        "phone_number": "32133213213",
        "role": "driver",
    }
    driver, _ = User.objects.get_or_create(
        email="drivertest@test.com", defaults=driver_default_kwargs
    )
    return driver


@pytest.fixture
def create_rider():
    rider_default_kwargs = {
        "password": "password1234",
        "first_name": "ridertest_firstname",
        "last_name": "ridertest_lastname",
        "phone_number": "32133213213",
        "role": "rider",
    }
    rider, _ = User.objects.get_or_create(
        email="ridertest@test.com", defaults=rider_default_kwargs
    )
    return rider


@pytest.mark.django_db
def test_sorted_by_distance_pagination(create_admin, create_driver, create_rider):
    client = APIClient()

    login_url = reverse("my_token_obtain_pair")
    response = client.post(
        login_url, {"email": "admin_test@admin.com", "password": "1234"}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    access_token = tokens["access"]

    client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

    # Create sample rides
    Ride.objects.create(
        status="en-route",
        pickup_latitude=14.624541,
        pickup_longitude=121.130679,
        dropoff_latitude=14.684959,
        dropoff_longitude=14.684959,
        pickup_time="2024-08-01T03:25:10Z",
        id_rider=create_rider,
        id_driver=create_driver,
    )
    Ride.objects.create(
        status="pickup",
        pickup_latitude=14.707641,
        pickup_longitude=121.01347,
        dropoff_latitude=14.684959,
        dropoff_longitude=14.684959,
        pickup_time="2024-08-01T03:25:10Z",
        id_rider=create_rider,
        id_driver=create_driver,
    )
    Ride.objects.create(
        status="pickup",
        pickup_latitude=14.710000,
        pickup_longitude=121.020000,
        dropoff_latitude=14.720000,
        dropoff_longitude=121.030000,
        pickup_time="2024-08-01T03:30:10Z",
        id_rider=create_rider,
        id_driver=create_driver,
    )

    def get_page_data(url, latitude, longitude, per_page):
        response = client.get(
            url, {"latitude": latitude, "longitude": longitude, "per_page": per_page}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "count" in data
        assert "per_page" in data
        assert "next_page" in data
        assert "previous_page" in data
        assert "total_pages" in data
        assert "data" in data
        assert "page" in data

        return data

    def check_page_data(page_data, latitude, longitude):
        rides_data = page_data["data"]  # Use "data" for paginated data

        # Calculate and sort the data, use is_for_test if data is list of dictionary
        sorted_data = calculate_and_sort_by_distance(
            rides_data, latitude=latitude, longitude=longitude, is_for_test=True
        )

        # Check sorting
        distances = [item.get("distance") for item in sorted_data]
        assert distances == sorted(
            distances, key=lambda x: x if x is not None else float("inf")
        )

        # Verify that each item has the correct fields
        for item in rides_data:
            assert "id_ride" in item
            assert "status" in item
            assert "pickup_latitude" in item
            assert "pickup_longitude" in item

        # Check pagination
        per_page = int(page_data.get("per_page", 1))
        page_number = int(page_data.get("page"))

        start_index = (page_number - 1) * per_page
        end_index = start_index + per_page

        assert rides_data == sorted_data[start_index:end_index]

        return sorted_data

    # Initial URL and coordinates
    latitude, longitude = 14.624458, 121.136387
    per_page = 1
    url = reverse("ride-list")
    page_data = get_page_data(url, latitude, longitude, per_page)
    check_page_data(page_data, latitude, longitude)

    # Check all subsequent pages
    next_page_url = page_data.get("next_page")  # Use "next_page" for the next page URL
    while next_page_url:
        response = client.get(
            next_page_url, {"latitude": latitude, "longitude": longitude}
        )
        response_next_data = response.json()
        check_page_data(response_next_data, latitude, longitude)
        next_page_url = response_next_data.get(
            "next_page"
        )  # Use "next_page" for the next page URL
