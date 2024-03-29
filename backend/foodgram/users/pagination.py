from rest_framework.pagination import PageNumberPagination


class CustomLimitPaginator(PageNumberPagination):
    page_size_query_param = 'limit'
