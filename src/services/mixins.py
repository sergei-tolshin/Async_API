from typing import Optional


class ListModelMixin:
    async def list(self, params: dict) -> Optional[dict]:
        # Получает список объектов с пагинацией
        query = await self.get_query(params)
        queryset = await self.data_manager.search(self.index, query)
        if not queryset:
            return None

        page = self.paginator.get_paginated_response(queryset)
        return page


class RetrieveModelMixin:
    # Возвращает экземпляр.
    # Он опционален, так как экземпляр может отсутствовать в базе
    async def retrieve(self, id: str) -> Optional[dict]:
        instance = await self.data_manager.get_object(self.index, id)
        if not instance:
            return None
        serializer = await self.get_serializer(instance)
        return serializer
