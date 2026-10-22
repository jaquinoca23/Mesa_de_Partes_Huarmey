from rest_framework.pagination import PageNumberPagination


class PaginacionEstandar(PageNumberPagination):
    """Listas de a 20 registros. Respuesta: { count, next, previous, results }."""

    page_size = 20
    page_size_query_param = 'por_pagina'
    max_page_size = 100
