from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

DEFAULT_PAGE = 1


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "pages": self.page.paginator.num_pages,
                "current_page": int(self.request.GET.get("page", DEFAULT_PAGE)),
                "page_size": int(self.request.GET.get("page_size", self.page_size)),
                "total": self.page.paginator.count,
                "results": data,
            }
        )
