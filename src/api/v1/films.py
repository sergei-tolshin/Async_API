from http import HTTPStatus
from typing import Optional

from core.paginator import Paginator
from core.utils.translation import gettext_lazy as _
from fastapi import APIRouter, Depends, HTTPException, Request
from models.film import FilmDetailsResponseModel, FilmPagination
from services.films import FilmService, get_film_service

from .utils.base import SearchQuery
from .utils.films import Filter, Sort

router = APIRouter()


@router.get('/search',
            response_model=FilmPagination,
            summary='Поиск по фильмам',
            description='Поиск по фильмам с постраничным разбиением',
            )
async def search_films(
    request: Request,
    obj_service: FilmService = Depends(get_film_service),
    query: SearchQuery = Depends(),
    paginator: Paginator = Depends(),
) -> FilmPagination:
    params = {
        'search_text': query.search_text,
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }
    obj_service.data_manager.request = request
    obj_service.paginator = paginator
    objects: Optional[dict] = await obj_service.list(params)
    if not objects:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('films_not_found'))

    return objects


@router.get('/{film_id}',
            response_model=FilmDetailsResponseModel,
            summary='Подробная информация о фильме',
            description='Вывод подробной информации о фильме',
            response_description=("uuid, название, описание, рейтинг, "
                                  "актеры, режиссеры, сценаристы")
            )
async def details(
    request: Request,
    film_id: str,
    obj_service: FilmService = Depends(get_film_service)
) -> FilmDetailsResponseModel:
    obj_service.data_manager.request = request
    obj = await obj_service.retrieve(film_id)
    if not obj:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('film_not_found'))

    return obj


@router.get('/',
            response_model=FilmPagination,
            summary='Список фильмов',
            description='Список фильмов с постраничным разбиением',
            response_description='uuid, название, рейтинг'
            )
async def list(
        request: Request,
        obj_service: FilmService = Depends(get_film_service),
        _filter: Filter = Depends(),
        sort: Sort = Depends(),
        paginator: Paginator = Depends(),
) -> FilmPagination:
    params: dict = {
        'filter[genre]': _filter.filter,
        'sort': sort.sort,
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }
    obj_service.data_manager.request = request
    obj_service.paginator = paginator
    objects: Optional[dict] = await obj_service.list(params)
    if not objects:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('films_not_found'))

    return objects
