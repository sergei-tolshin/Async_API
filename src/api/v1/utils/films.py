from typing import Optional

from fastapi import Query

DEFAULT_SORT_ORDER = '-imdb_rating'


class Sort:
    """Добавление сортировки в параметры запроса"""

    def __init__(self, sort: str = DEFAULT_SORT_ORDER):
        self.sort_params = sort


class Filter:
    """Добавление фильтрации в параметры запроса"""

    def __init__(self,
                 _filter: Optional[str] = Query(None, alias='filter[genre]')):
        self.filter = _filter
