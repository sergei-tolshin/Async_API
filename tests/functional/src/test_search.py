import orjson
import pytest
import factory
from faker import Factory as FakerFactory
from functional.settings import config
from functional.testdata.films.factories import FilmFactory
from functional.testdata.films.models import FilmModel, FilmPagination
from functional.testdata.films.schema import SCHEMA as films_schema
from functional.testdata.persons.factories import PersonFactory
from functional.testdata.persons.models import PersonModel, PersonPagination
from functional.testdata.persons.schema import SCHEMA as persons_schema
from functional.utils.utils import hash_key

PESON_INDEX = config.ELASTIC_INDEX['persons']
FILM_INDEX = config.ELASTIC_INDEX['films']

fake = FakerFactory.create()


@pytest.fixture(scope='class')
async def persons_index(es_client):
    await es_client.indices.create(index=PESON_INDEX, body=persons_schema)
    yield
    await es_client.indices.delete(index=PESON_INDEX)


@pytest.fixture(scope='class')
async def films_index(es_client):
    await es_client.indices.create(index=FILM_INDEX, body=films_schema)
    yield
    await es_client.indices.delete(index=FILM_INDEX)


@pytest.mark.usefixtures('persons_index', 'films_index')
class TestSearchAPI:
    @pytest.fixture(autouse=True)
    async def clear_storage(self, es_client):
        query = {"query": {"match_all": {}}}
        await es_client.delete_by_query(index=PESON_INDEX, body=query,
                                        refresh=True)
        await es_client.delete_by_query(index=FILM_INDEX, body=query,
                                        refresh=True)

    @pytest.fixture(autouse=True)
    async def clear_cache(self, cache):
        await cache.flushall()

    @pytest.mark.asyncio
    async def test_01_person_search(self, make_get_request, bulk):
        persons = PersonFactory.build_batch(10, full_name=factory.LazyAttribute(
            lambda x: 'Name ' + fake.name()))
        await bulk(index=PESON_INDEX, objects=persons)
        persons = PersonFactory.build_batch(20)
        await bulk(index=PESON_INDEX, objects=persons)

        path = '/api/v1/persons/search'

        response = await make_get_request(path)
        assert response.status == 422, \
            'Запрос без параметров возвращает статус 422'

        params = {'query': persons[3].full_name, }
        response = await make_get_request(path, params)
        data = response.body
        assert PersonPagination(**data), \
            'Данные не соответствуют модели'

        assert data['results'][0] == persons[3], \
            'Найденные данные не совпадают'

        params = {
            'query': 'Name',
            'page[size]': 5
        }
        response = await make_get_request(path, params)
        data = response.body
        assert data['count'] == 10
        assert len(data['results']) == params['page[size]'], \
            'Количество результатов не совпадает с количеством на странице'

        params = {'query': 'UnknownPerson123'}
        response = await make_get_request(path, params)
        data = response.body
        assert len(data['results']) == 0, \
            'Значение параметра `results` не правильное'

    @pytest.mark.asyncio
    async def test_02_person_search_cache(self, make_get_request, bulk, cache):
        persons = PersonFactory.build_batch(5)
        await bulk(index=PESON_INDEX, objects=persons)

        path = '/api/v1/persons/search'
        params = {
            'query': persons[2].full_name,
            'page[number]': '1',
            'page[size]': '10'
        }
        response = await make_get_request(path, params)
        data = response.body
        key = hash_key(PESON_INDEX, {'path': path, 'params': params})
        data_cache = await cache.get(key=key)
        results = [PersonModel(**_).dict()
                   for _ in orjson.loads(data_cache)['results']]
        assert data_cache is not None, \
            'Проверьте, что при запросе из кэша возвращаете данные объекта.'
        assert results == data['results'], \
            'Данные обекта в elastic не совпадают с данными в кэше'
        await cache.delete(key=key)
        assert await cache.get(key=key) is None, \
            'Проверьте, что при DELETE удаляете объект из кэша'

    @pytest.mark.asyncio
    async def test_03_films_search(self, make_get_request, bulk):
        films = FilmFactory.build_batch(10, title=factory.LazyAttribute(
            lambda x: 'Title ' + fake.name()))
        await bulk(index=FILM_INDEX, objects=films)
        films = FilmFactory.build_batch(20)
        await bulk(index=FILM_INDEX, objects=films)

        path = '/api/v1/films/search'

        response = await make_get_request(path)
        assert response.status == 422, \
            'Запрос без параметров возвращает статус 422'

        params = {'query': films[3].title}
        response = await make_get_request(path, params)
        data = response.body
        assert FilmPagination(**data), \
            'Данные не соответствуют модели'

        assert data['results'][0] == films[3], \
            'Найденные данные не совпадают'

        params = {
            'query': 'Title',
            'page[size]': 5
        }
        response = await make_get_request(path, params)
        data = response.body
        assert data['count'] == 10
        assert len(data['results']) == params['page[size]'], \
            'Количество результатов не совпадает с количеством на странице'

        params = {'query': 'UnknownFilm123'}
        response = await make_get_request(path, params)
        data = response.body
        assert len(data['results']) == 0, \
            'Значение параметра `results` не правильное, ' \
            'Должно быть 0 при отсетствии результатов'

    @pytest.mark.asyncio
    async def test_04_films_search_cache(self, make_get_request, bulk, cache):
        films = FilmFactory.build_batch(5)
        await bulk(index=FILM_INDEX, objects=films)

        path = '/api/v1/films/search'
        params = {
            'query': films[2].title,
            'page[number]': '1',
            'page[size]': '10'
        }
        response = await make_get_request(path, params)
        data = response.body
        key = hash_key(FILM_INDEX, {'path': path, 'params': params})
        data_cache = await cache.get(key=key)
        print(data_cache)
        results = [FilmModel(**_).dict()
                   for _ in orjson.loads(data_cache)['results']]
        assert data_cache is not None, \
            'Проверьте, что при запросе из кэша возвращаете данные объекта.'
        assert results == data['results'], \
            'Данные обекта в elastic не совпадают с данными в кэше'
        await cache.delete(key=key)
        assert await cache.get(key=key) is None, \
            'Проверьте, что при DELETE удаляете объект из кэша'
