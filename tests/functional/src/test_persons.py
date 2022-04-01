import orjson
import pytest
from functional.models.film import FilmModel, FilmPagination
from functional.models.person import (PersonDetailsModel, PersonModel,
                                      PersonPagination)
from functional.settings import config
from functional.utils.utils import hash_key


class TestPersonsAPI:
    index = config.ELASTIC_PERSON_INDEX

    """ Вывести всех людей """
    @pytest.mark.asyncio
    async def test_01_person(self, make_get_request, cache):
        path = '/api/v1/persons/'

        response = await make_get_request(path)
        assert response.status == 200, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращает статус 200'

        data = response.body
        assert PersonPagination(**data), \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Данные не соответствуют модели'
        assert 'count' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `count`'
        assert 'total_pages' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `total_pages`'
        assert 'next' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `next`'
        assert 'previous' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `previous`'
        assert 'results' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `results`'
        assert data['count'] == 4166, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Значение параметра `count` не правильное'
        assert type(data['results']) == list, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Тип параметра `results` должен быть список'
        assert len(data['results']) == 10, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Значение параметра `results` не правильное'

        params = {"filter[role]": "director"}
        response = await make_get_request(path, params)
        data = response.body
        assert data['count'] == 700, \
            'Проверьте, что при GET запросе `/api/v1/persons/` ' \
            'Результаты фильтруются по `filter[role]` параметру `director`'

        params = {'filter[role]': 'actor'}
        response = await make_get_request(path, params)
        data = response.body
        assert data['count'] == 2682, \
            'Проверьте, что при GET запросе `/api/v1/persons/` ' \
            'Результаты фильтруются по `filter[role]` параметру `actor`'

        params = {'filter[role]': 'writer'}
        response = await make_get_request(path, params)
        data = response.body
        assert data['count'] == 1191, \
            'Проверьте, что при GET запросе `/api/v1/persons/` ' \
            'Результаты фильтруются по `filter[role]` параметру `writer`'

        params = {'page[number]': '417'}
        response = await make_get_request(path, params)
        data = response.body
        assert len(data['results']) == 6, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращаете данные с пагинацией. ' \
            'Значение параметра `results` не правильное'

        params = {'page[number]': '500'}
        response = await make_get_request(path, params)
        assert response.status == 404, \
            'Проверьте, что при GET запросе `/api/v1/persons/` возвращает статус 404 при неверной странице'

        params = {'page[size]': '50'}
        response = await make_get_request(path, params)
        data = response.body
        assert data['total_pages'] == 84, \
            'Проверьте, что при GET запросе `/api/v1/persons/` меняется количество сраниц при изменение `page[size]`'

        # поиск с учётом кеша в Redis
        key = hash_key(self.index, {'path': path, 'params': params})
        data_cache = await cache.get(key=key)
        results = [PersonModel(**_).dict()
                   for _ in orjson.loads(data_cache)['results']]
        assert data_cache is not None, \
            'Проверьте, что при запросе из кэша возвращаете данные объекта.'
        assert results == data['results'], \
            'Проверьте, что при запросе из кэша возвращаете данные объекта. ' \
            'Данные обекта в elastic не совпадают с данными в кэше'
        await cache.delete(key=key)
        assert await cache.get(key=key) is None, \
            'Проверьте, что при DELETE удаляете объект из кэша'

    """ Поиск конкретного человека """
    @pytest.mark.asyncio
    async def test_02_person_detail(self, make_get_request, read_case, cache):
        object = await read_case('persons/case_get_by_id.json')

        path = f"/api/v1/persons/{object['id']}/"

        response = await make_get_request(path)
        assert response.status == 200, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/` возвращает статус 200'

        data = response.body
        assert PersonDetailsModel(**data), \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/` возвращаете данные с пагинацией. ' \
            'Данные не соответствуют модели'
        assert type(data.get('id')) == str, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/` возвращаете данные объекта. ' \
            'Значение `id` нет или не является строкой.'
        assert data.get('full_name') == object['full_name'], \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/` возвращаете данные объекта. ' \
            'Значение `full_name` неправильное.'
        assert data.get('roles') == object['roles'], \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/` возвращаете данные объекта. ' \
            'Значение `roles` неправильное.'
        assert data.get('film_ids') == object['film_ids'], \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/` возвращаете данные объекта. ' \
            'Значение `film_ids` неправильное.'

        # поиск с учётом кеша в Redis
        key = hash_key(self.index, object['id'])
        data_cache = await cache.get(key=key)
        assert await cache.get(key=key) is not None, \
            'Проверьте, что при запросе из кэша возвращаете данные объекта.'
        assert orjson.loads(data_cache) == data, \
            'Проверьте, что при запросе из кэша возвращаете данные объекта. ' \
            'Данные обекта в elastic не совпадают с данными в кэше'
        await cache.delete(key=key)
        assert await cache.get(key=key) is None, \
            'Проверьте, что при DELETE удаляете объект из кэша'

    """ Поиск всех фильмов с участием человека """
    @pytest.mark.asyncio
    async def test_03_person_films(self, make_get_request, read_case, cache):
        object = await read_case('persons/case_get_films.json')

        path = f"/api/v1/persons/{object['id']}/film/"

        response = await make_get_request(path)
        assert response.status == 200, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращает статус 200'

        data = response.body
        assert FilmPagination(**data), \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Данные не соответствуют модели'
        assert 'count' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `count`'
        assert 'total_pages' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `total_pages`'
        assert 'next' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `next`'
        assert 'previous' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `previous`'
        assert 'results' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Не найден параметр `results`'
        assert data['count'] == 6, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Значение параметра `count` не правильное'
        assert type(data['results']) == list, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Тип параметра `results` должен быть список'
        assert len(data['results']) == 6, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращаете данные с пагинацией. ' \
            'Значение параметра `results` не правильное'

        params = {'page[number]': '2'}
        response = await make_get_request(path, params)
        assert response.status == 404, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` возвращает статус 404 при указании несуществующей страницы'

        params = {'page[size]': '2'}
        response = await make_get_request(path, params)
        data = response.body
        assert data['total_pages'] == 3, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` меняется количество сраниц при изменение `page[size]`'
        assert len(data['results']) == 2, \
            'Проверьте, что при GET запросе `/api/v1/persons/{person_id}/film/` количество результатов ' \
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

    """ Поиск человека или людей по фразе """
    @pytest.mark.asyncio
    async def test_04_person_search(self, make_get_request, read_case, cache):
        object = await read_case('persons/case_get_search.json')

        path = '/api/v1/persons/search'

        params = {'query': 'Samuli Torssonen'}
        response = await make_get_request(path, params)
        assert response.status == 200, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращает статус 200'

        data = response.body
        assert PersonPagination(**data), \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Данные не соответствуют модели'
        assert 'count' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `count`'
        assert 'total_pages' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `total_pages`'
        assert 'next' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `next`'
        assert 'previous' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `previous`'
        assert 'results' in data, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Не найден параметр `results`'
        assert data['count'] == 8, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Значение параметра `count` не правильное'
        assert type(data['results']) == list, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Тип параметра `results` должен быть список'
        assert len(data['results']) == 8, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Значение параметра `results` не правильное'
        assert data['results'][1]['id'] == object['id'], \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Значение параметра `id` не правильное'
        assert type(data['results'][1]['roles']) == list, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Тип параметра `roles` должен быть список'
        assert type(data['results'][1]['film_ids']) == list, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Тип параметра `film_ids` должен быть список'

        params = {'query': 'persons_not_found'}
        response = await make_get_request(path, params)
        data = response.body
        assert len(data['results']) == 0, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращаете данные с пагинацией. ' \
            'Значение параметра `results` не правильное'

        params = {'query': 'Samuli Torssonen', 'page[number]': '2'}
        response = await make_get_request(path, params)
        assert response.status == 404, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` возвращает статус 404 при указании несуществующей страницы'

        params = {'query': 'Samuli Torssonen', 'page[size]': '2'}
        response = await make_get_request(path, params)
        data = response.body
        assert data['total_pages'] == 4, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` меняется количество сраниц при изменение `page[size]`'
        assert len(data['results']) == 2, \
            'Проверьте, что при GET запросе `/api/v1/persons/search` количество результатов ' \
            'соответствует `page[size]`'

        # поиск с учётом кеша в Redis
        key = hash_key(self.index, {'path': path, 'params': params})
        data_cache = await cache.get(key=key)
        results = [PersonModel(**_).dict()
                   for _ in orjson.loads(data_cache)['results']]
        assert data_cache is not None, \
            'Проверьте, что при запросе из кэша возвращаете данные объекта.'
        assert results == data['results'], \
            'Проверьте, что при запросе из кэша возвращаете данные объекта. ' \
            'Данные обекта в elastic не совпадают с данными в кэше'
        await cache.delete(key=key)
        assert await cache.get(key=key) is None, \
            'Проверьте, что при DELETE удаляете объект из кэша'
