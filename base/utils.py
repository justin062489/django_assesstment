from rest_framework.pagination import PageNumberPagination
from haversine import haversine
from typing import List, Dict, Optional


def paginator(
    per_page: int, data: List, serializer: object, request: object, context=None
):
    paginator = PageNumberPagination()
    paginator.page_size = per_page
    paginated_data = paginator.paginate_queryset(data, request)
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
    paginated_data: List[Dict],
    latitude: float,
    longitude: float,
) -> List[Dict]:

    for item in paginated_data["data"]:
        try:
            ## Add key distance and integrate value
            item["distance"] = haversine(
                (latitude, longitude),
                (item["pickup_latitude"], item["pickup_longitude"]),
            )
        except (ValueError, TypeError, KeyError) as e:
            print(f"Error calculating distance for item {item}: {e}")
            item["distance"] = None

    ## Sort Data by the added distance value
    ## float(inf) incase there if distance key is none.
    paginated_data["data"] = sorted(
        paginated_data["data"], key=lambda x: x.get("distance", float("inf"))
    )
    return paginated_data
