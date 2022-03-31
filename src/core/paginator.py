import math
from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException, Query
from pydantic import BaseModel

from core import config
from core.utils.translation import gettext_lazy as _


class PaginationMixin(BaseModel):
    """Модель ответа API с пагинацией"""
    count: int
    total_pages: int
    next: Optional[int] = None
    previous: Optional[int] = None


class Paginator:
    """Добавление пагинации в параметры запроса"""

    def __init__(
        self,
        page_number: int = Query(None, alias='page[number]', ge=1),
        page_size: int = Query(
            None, alias='page[size]', ge=1, le=config.MAX_PAGE_SIZE),
    ) -> None:
        self.page_number = page_number or 1
        self.page_size = page_size or config.PAGE_SIZE

    def get_paginated_response(self, queryset) -> dict:
        next_page, previous_page = None, None
        if self.page_number > 1:
            previous_page = self.page_number - 1
        previous_items = (self.page_number - 1) * self.page_size
        if previous_items + len(queryset['results']) < queryset['count']:
            next_page = self.page_number + 1
        total_pages: int = int(
            math.ceil(queryset['count'] / float(self.page_size)))
        if queryset['count'] > 0 and self.page_number > total_pages:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=_('Invalid page'))
        if queryset['count'] == 0 and self.page_number > 1:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=_('Invalid page'))
        return {
            'count': queryset['count'],
            'total_pages': total_pages,
            'next': next_page,
            'previous': previous_page,
            'results': queryset['results'],
        }
