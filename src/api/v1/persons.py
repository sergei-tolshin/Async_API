from http import HTTPStatus
from typing import Optional

from core.paginator import Paginator
from core.utils.translation import gettext_lazy as _
from fastapi import APIRouter, Depends, HTTPException
from models.person import (PersonDetailsResponseModel, PersonElasticModel,
                           PersonFilmPagination, PersonPagination)
from services.persons import PersonService, get_person_service

from .utils.base import SearchQuery
from .utils.persons import Filter

router = APIRouter()


@router.get('/search',
            response_model=PersonPagination,
            summary='Поиск по персонажам',
            description='Поиск по персонажам с постраничным разбиением',
            )
async def search(
    obj_service: PersonService = Depends(get_person_service),
    query: SearchQuery = Depends(),
    paginator: Paginator = Depends(),
) -> PersonPagination:
    params = {
        'search_text': query.search_text,
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }

    objects = await obj_service.get_list(params)
    if not objects:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('persons_not_found'))
    return objects


@router.get('/{person_id}',
            response_model=PersonDetailsResponseModel,
            summary='Подробная информация о персонаже',
            description='Вывод подробной информации о персонаже',
            response_description='uuid, имя, роль, фильмы'
            )
async def details(
    person_id: str,
    obj_service: PersonService = Depends(get_person_service)
) -> PersonDetailsResponseModel:
    obj = await obj_service.get_by_id(id=person_id, model=PersonElasticModel)
    if not obj:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('person_not_found'))
    return PersonDetailsResponseModel(
        id=obj.id,
        full_name=obj.full_name,
        roles=obj.roles,
        film_ids=obj.film_ids,
        actor_film_ids=obj.actor_film_ids,
        director_film_ids=obj.director_film_ids,
        writer_film_ids=obj.writer_film_ids,
    )


@router.get('/{person_id}/film/',
            response_model=PersonFilmPagination,
            summary='Фильмы с участием персонажа',
            description='Вывод списка фильмов с участием персонажа',
            response_description='uuid, название, рейтинг'
            )
async def person_films(
    person_id: str,
    obj_service: PersonService = Depends(get_person_service),
    paginator: Paginator = Depends(),
) -> PersonFilmPagination:
    person = await obj_service.get_by_id(id=person_id,
                                         model=PersonElasticModel)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('person_not_found'))
    params: dict = {
        '_index': 'movies',
        'query_body': {'query': {'ids': {'values': person.film_ids}}},
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }
    films = await obj_service.get_films(person_id, params)
    return films


@router.get('/',
            response_model=PersonPagination,
            summary='Список персонажей',
            description='Список персонажей с постраничным разбиением',
            response_description='uuid, имя, роли'
            )
async def list(
    obj_service: PersonService = Depends(get_person_service),
    _filter: Filter = Depends(),
    paginator: Paginator = Depends(),
) -> PersonPagination:
    query_body = {'query': {'term': {'roles': _filter.filter}}
                  } if _filter.filter else None
    params: dict = {
        'query_body': query_body,
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }
    objects: Optional[dict] = await obj_service.get_list(params)
    if not objects:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('persons_not_found'))
    return objects
