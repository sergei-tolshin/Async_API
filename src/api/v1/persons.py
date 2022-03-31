from http import HTTPStatus
from typing import Optional

from core.paginator import Paginator
from core.utils.translation import gettext_lazy as _
from fastapi import APIRouter, Depends, HTTPException, Request
from models.person import (PersonDetailsResponseModel, PersonFilmPagination,
                           PersonPagination)
from services.persons import PersonService, get_person_service

from .utils.base import SearchQuery
from .utils.persons import Filter

router = APIRouter()


@router.get('/search',
            response_model=PersonPagination,
            summary='Поиск по людям',
            description='Поиск по людям с постраничным разбиением',
            response_description='uuid, имя, роли, фильмы',
            tags=['Люди']
            )
async def search(
    request: Request,
    service: PersonService = Depends(get_person_service),
    query: SearchQuery = Depends(),
    paginator: Paginator = Depends(),
) -> PersonPagination:
    params = {
        'search_text': query.search_text,
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }
    service.request = request
    service.paginator = paginator
    objects: Optional[dict] = await service.list(params)
    if not objects:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('persons_not_found'))
    return objects


@router.get('/{person_id}',
            response_model=PersonDetailsResponseModel,
            summary='Подробная информация о человеке',
            description='Вывод подробной информации о человеке',
            response_description='uuid, имя, роль, фильмы, фильмы по ролям',
            tags=['Люди']
            )
async def details(
    request: Request,
    person_id: str,
    service: PersonService = Depends(get_person_service)
) -> PersonDetailsResponseModel:
    service.data_manager.request = request
    obj = await service.retrieve(person_id)
    if not obj:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('person_not_found'))
    return obj


@router.get('/{person_id}/film/',
            response_model=PersonFilmPagination,
            summary='Фильмы с участием человека',
            description=("Вывод списка фильмов с участием человека"
                         "с постраничным разбиением"),
            response_description='uuid, название, рейтинг',
            tags=['Люди']
            )
async def person_films(
    request: Request,
    person_id: str,
    service: PersonService = Depends(get_person_service),
    paginator: Paginator = Depends(),
) -> PersonFilmPagination:
    person = await service.retrieve(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('person_not_found'))
    params: dict = {
        '_index': 'movies',
        'query_body': {'query': {'ids': {'values': person.film_ids}}},
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }
    service.request = request
    service.paginator = paginator
    films: Optional[dict] = await service.list(params)
    return films


@router.get('/',
            response_model=PersonPagination,
            summary='Список людей',
            description=("Список людей с постраничным разбиением "
                         "и фильтром по ролям"),
            response_description='uuid, имя, роли',
            tags=['Люди']
            )
async def list(
    request: Request,
    service: PersonService = Depends(get_person_service),
    _filter: Filter = Depends(),
    paginator: Paginator = Depends(),
) -> PersonPagination:
    service.request = request
    service.paginator = paginator

    query_body = {'query': {'term': {'roles': _filter.filter}}
                  } if _filter.filter else None
    params: dict = {
        'query_body': query_body,
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }

    objects: Optional[dict] = await service.list(params)
    if not objects:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('persons_not_found'))
    return objects
