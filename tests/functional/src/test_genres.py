import orjson
import pytest
from functional.models.genre import GenreModel, GenreDetailsModel
from functional.settings import config
from functional.utils.utils import hash_key


class TestGenresAPI:
    index = config.ELASTIC_GENRE_INDEX

    """ Вывести все жанры """
    @pytest.mark.asyncio
    async def test_01_genres(self, make_get_request, read_case, cache):
        pass

    """ Поиск конкретного жанра """
    @pytest.mark.asyncio
    async def test_02_genres_detail(self, make_get_request, read_case, cache):
        pass
