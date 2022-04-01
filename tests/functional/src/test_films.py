import orjson
import pytest
from functional.models.film import FilmModel, FilmPagination
from functional.settings import config
from functional.utils.utils import hash_key


class TestFilmsAPI:
    index = config.ELASTIC_FILMS_INDEX

    """ Вывести все фильмы """
    @pytest.mark.asyncio
    async def test_01_films(self, make_get_request, read_case, cache):
        pass

    """ Поиск конкретного фильма """
    @pytest.mark.asyncio
    async def test_02_films_detail(self, make_get_request, read_case, cache):
        pass

    """ Поиск фильма или фильмов по фразе """
    @pytest.mark.asyncio
    async def test_03_films_search(self, make_get_request, read_case, cache):
        object = await read_case('films/case_get_search.json')

        path = '/api/v1/films/search'

        params = {'query': 'Lego'}
        response = await make_get_request(path, params)
        assert response.status == 200, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращает статус 200'

        data = response.body
        assert FilmPagination(**data), \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Данные не соответствуют модели'
        assert 'count' in data, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `count`'
        assert 'total_pages' in data, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `total_pages`'
        assert 'next' in data, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `next`'
        assert 'previous' in data, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `previous`'
        assert 'results' in data, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `results`'
        assert data['count'] == 26, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Значение параметра `count` не правильное'
        assert type(data['results']) == list, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Тип параметра `results` должен быть список'
        assert len(data['results']) == 10, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Значение параметра `results` не правильное'
        assert data['results'][1]['id'] == object['results'][1]['id'], \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Значение параметра `id` не правильное'
        assert type(data['results'][1]['imdb_rating']) == float, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Тип параметра `imdb_rating` должен быть float'

        params = {'query': 'films_not_found'}
        response = await make_get_request(path, params)
        data = response.body
        assert len(data['results']) == 0, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращаете данные с пагинацией. ' \
            'Значение параметра `results` не правильное'

        params = {'query': 'Lego', 'page[number]': '4'}
        response = await make_get_request(path, params)
        assert response.status == 404, \
            'Проверьте, что при GET запросе `/api/v1/films/search` возвращает статус 404 при указании несуществующей страницы'

        params = {'query': 'Lego', 'page[size]': '5'}
        response = await make_get_request(path, params)
        data = response.body
        assert data['total_pages'] == 6, \
            'Проверьте, что при GET запросе `/api/v1/films/search` меняется количество сраниц при изменение `page[size]`'
        assert len(data['results']) == 5, \
            'Проверьте, что при GET запросе `/api/v1/films/search` количество результатов ' \
            'соответствует `page[size]`'

        # поиск с учётом кеша в Redis
        key = hash_key(self.index, {'path': path, 'params': params})
        data_cache = await cache.get(key=key)
        results = [FilmModel(**_).dict()
                   for _ in orjson.loads(data_cache)['results']]
        assert data_cache is not None, \
            'Проверьте, что при запросе из кэша возвращаете данные объекта.'
        assert results == data['results'], \
            'Проверьте, что при запросе из кэша возвращаете данные объекта. ' \
            'Данные обекта в elastic не совпадают с данными в кэше'
        await cache.delete(key=key)
        assert await cache.get(key=key) is None, \
            'Проверьте, что при DELETE удаляете объект из кэша'
