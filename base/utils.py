from rest_framework.pagination import PageNumberPagination


def paginator(
    per_page: int, data: object, serializer: object, request: object, context=None
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
