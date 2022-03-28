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
        page_size:  int = Query(config.PAGE_SIZE, alias='page[size]', ge=1),
    ) -> None:
        self.page_number = page_number
        self.page_size = page_size


def get_pagination(
    objects,
    count: int,
    page: int = 1,
    page_size: int = 20
) -> dict:
    next_page, prev_page = None, None
    if page > 1:
        prev_page = page - 1
    prev_items = (page - 1) * page_size
    if prev_items + len(objects) < count:
        next_page = page + 1
    total_pages: int = int(math.ceil(count / float(page_size)))
    return {
        'count': count,
        'total_pages': total_pages,
        'prev': prev_page,
        'next': next_page,
        'results': objects,
    }
