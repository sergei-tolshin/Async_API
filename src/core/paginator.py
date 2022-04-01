import math
from http import HTTPStatus
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from fastapi import HTTPException, Query
from pydantic import BaseModel

from core import config
from core.utils.translation import gettext_lazy as _


class PaginationMixin(BaseModel):
    """Модель ответа API с пагинацией"""
    count: int
    total_pages: int
    next: Optional[str] = None
    previous: Optional[str] = None


class Paginator:
    """Добавление пагинации в параметры запроса"""

    def __init__(
        self,
        page_number: int = Query(
            None,
            title='Номер страницы',
            description='Номер страницы',
            alias='page[number]',
            ge=1),
        page_size: int = Query(
            None,
            title='Количество результатов на странице',
            description='Количество результатов на странице',
            alias='page[size]',
            ge=1,
            le=config.MAX_PAGE_SIZE),
    ) -> None:
        self.page_number = page_number or 1
        self.page_size = page_size or config.PAGE_SIZE

    async def get_paginated_response(self, request, queryset) -> dict:
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

        next_page_url = await self.get_page_url(request, next_page)
        previous_page_url = await self.get_page_url(request, previous_page)

        return {
            'count': queryset['count'],
            'total_pages': total_pages,
            'next': next_page_url,
            'previous': previous_page_url,
            'results': queryset['results'],
        }

    async def get_page_url(self, request, page):
        if page is None:
            return None

        url = str(request.url)
        url_parts = list(urlparse(url))
        params = {'page[number]': page}
        query = dict(parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query, safe='[]')
        return urlunparse(url_parts)
