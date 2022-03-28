from http import HTTPStatus
from typing import List
from uuid import UUID

from core.paginator import Paginator
from core.utils.translation import gettext_lazy as _
from fastapi import APIRouter, Depends, HTTPException
from models.film import FilmResponseModel
from services.films import FilmService, get_film_service

from .utils.base import SearchQuery
from .utils.films import Filter, Sort

router = APIRouter()


@router.get('/', response_model=List[FilmResponseModel],
            response_model_include={'id', 'title', 'imdb_rating'})
async def list_films(film_service: FilmService = Depends(get_film_service),
                     paginator: Paginator = Depends(),
                     sort: Sort = Depends(),
                     _filter: Filter = Depends()) -> List[FilmResponseModel]:

    query_params = {
        'sort': sort.sort_params,
        'filter[genre]': _filter.filter,
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
    }

    films = await film_service.get_films(query_params)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('films_not_found'))

    return (FilmResponseModel(**film.dict()) for film in films)


@router.get('/search', response_model=List[FilmResponseModel],
            response_model_include={'id', 'title', 'imdb_rating'})
async def search_films(
    film_service: FilmService = Depends(get_film_service),
    paginator: Paginator = Depends(),
    query: SearchQuery = Depends()
) -> List[FilmResponseModel]:

    query_params = {
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
        'query': query.search_text
    }

    films = await film_service.get_films(query_params)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('films_not_found'))

    return (FilmResponseModel(**film.dict()) for film in films)


@router.get('/{film_id}', response_model=FilmResponseModel)
async def film_details(
    film_id: UUID,
    film_service: FilmService = Depends(get_film_service)
) -> FilmResponseModel:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('film_not_found'))

    return FilmResponseModel(**film.dict())
