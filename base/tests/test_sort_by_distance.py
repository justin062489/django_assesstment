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

    Ride.objects.create(
        status="en-route",
        pickup_latitude=14.684959,
        pickup_longitude=121.031774,
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

    # Request the API endpoint
    url = reverse("ride-list")
    response = client.get(url, {"latitude": 14.695, "longitude": 121.025})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Verify pagination metadata
    assert "count" in data
    assert "per_page" in data
    assert "next_page" in data
    assert "previous_page" in data
    assert "total_pages" in data
    assert "data" in data

    def check_page_data(page_data, page_num):
        sorted_data = calculate_and_sort_by_distance(
            page_data["data"], latitude=14.695, longitude=121.025
        )

        assert len(sorted_data) == len(page_data["data"])

        distances = [item.get("distance") for item in sorted_data]
        assert distances == sorted(
            distances, key=lambda x: x if x is not None else float("inf")
        )

        for item in page_data["data"]:
            assert "id_ride" in item
            assert "status" in item
            assert "pickup_latitude" in item
            assert "pickup_longitude" in item

        return sorted_data

    sorted_data = check_page_data(data, page_num=1)

    # Check the next pages if they exist
    next_page_url = data.get("next_page")
    while next_page_url:
        response_next = client.get(next_page_url)
        assert response_next.status_code == status.HTTP_200_OK
        data_next = response_next.json()

        # Verify next page data
        sorted_data_next = check_page_data(
            data_next, page_num=len(sorted_data) // int(data["per_page"]) + 1
        )

        # Update the URL for the next page
        next_page_url = data_next.get("next_page")
