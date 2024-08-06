from rest_framework.pagination import PageNumberPagination
from haversine import haversine
from typing import List, Dict, Optional
from django.forms.models import model_to_dict


def paginator(
    per_page: int, data: List, serializer: object, request: object, context=None
):
    paginator = PageNumberPagination()
    paginator.page_size = per_page
    paginated_data = paginator.paginate_queryset(data, request)
    print(paginated_data, "from paginated data")
    serializer = serializer(paginated_data, many=True)
    response_data = {
        "count": paginator.page.paginator.count,
        "per_page": per_page,
        "next_page": paginator.get_next_link(),
        "previous_page": paginator.get_previous_link(),
        "total_pages": paginator.page.paginator.num_pages,
        "data": serializer.data,
    }
    return response_data


def calculate_and_sort_by_distance(
    queryset: List[Dict],
    latitude: float,
    longitude: float,
) -> List[Dict]:

    converted_queryset = ride_data_to_list(queryset)

    for item in converted_queryset:
        try:
            # Calculate distance and add it to the item
            item["distance"] = haversine(
                (latitude, longitude),
                (item["pickup_latitude"], item["pickup_longitude"]),
            )
        except (ValueError, TypeError, KeyError) as e:
            print(f"Error calculating distance for item {item}: {e}")
            item["distance"] = None

    # Sort the new list by the distance
    converted_queryset = sorted(
        converted_queryset, key=lambda x: x.get("distance", float("inf"))
    )

    return converted_queryset


def ride_data_to_list(queryset: List[object]):
    converted_queryset = []
    for ride in queryset:
        kwargs = {
            "id_ride": ride.id_ride,
            "status": ride.status,
            "pickup_latitude": ride.pickup_latitude,
            "pickup_longitude": ride.pickup_longitude,
            "dropoff_latitude": ride.dropoff_latitude,
            "dropoff_longitude": ride.dropoff_longitude,
            "pickup_time": ride.pickup_time,
            "today_ride_events": [
                {
                    "id_ride_event": event.id_ride_event,
                    "description": event.description,
                    "created_at": event.created_at,
                    "id_ride": event.id_ride,
                }
                for event in ride.today_ride_events
            ],
        }
        converted_queryset.append(kwargs)

    return converted_queryset
