import math
from typing import Optional

from fastapi import Query
from pydantic import BaseModel

from core import config


class PaginationMixin(BaseModel):
    """Модель ответа API с пагинацией"""
    count: int
    total_pages: int
    prev: Optional[int] = None
    next: Optional[int] = None


class Paginator:
    """Добавление пагинации в параметры запроса"""

    def __init__(
        self,
        page_number: int = Query(1, alias='page[number]', ge=1),
        page_size:  int = Query(
            config.PAGE_SIZE, alias='page[size]', ge=1, le=100),
    ) -> None:
        self.page_number = page_number
        self.page_size = page_size

    def get_paginated_response(self, queryset) -> dict:
        next_page, prev_page = None, None
        if self.page_number > 1:
            prev_page = self.page_number - 1
        prev_items = (self.page_number - 1) * self.page_size
        if prev_items + len(queryset['obj']) < queryset['count']:
            next_page = self.page_number + 1
        total_pages: int = int(
            math.ceil(queryset['count'] / float(self.page_size)))
        return {
            'count': queryset['count'],
            'total_pages': total_pages,
            'prev': prev_page,
            'next': next_page,
            'results': queryset['obj'],
        }
