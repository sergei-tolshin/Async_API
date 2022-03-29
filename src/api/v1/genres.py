from http import HTTPStatus
from typing import Optional

from core.paginator import Paginator
from core.utils.translation import gettext_lazy as _
from fastapi import APIRouter, Depends, HTTPException
from models.genre import GenreDetailsResponseModel, GenrePagination
from services.genres import GenreService, get_genre_service

from .utils.genres import Sort

router = APIRouter()


@router.get('/{genre_id}',
            response_model=GenreDetailsResponseModel,
            summary='Подробная информация о жанре',
            description='Вывод подробной информации о жанре',
            response_description='uuid, название, описание'
            )
async def details(
    genre_id: str,
    obj_service: GenreService = Depends(get_genre_service)
) -> GenreDetailsResponseModel:
    obj = await obj_service.retrieve(genre_id)
    if not obj:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('genre_not_found'))
    return obj


@router.get('/',
            response_model=GenrePagination,
            summary='Список жанров',
            description='Список жанров с постраничным разбиением',
            response_description='uuid, название'
            )
async def list(
    obj_service: GenreService = Depends(get_genre_service),
    paginator: Paginator = Depends(),
    sort: Sort = Depends(),
) -> GenrePagination:
    params: dict = {
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
        'sort': sort.sort,
    }
    obj_service.paginator = paginator
    objects: Optional[dict] = await obj_service.list(params)
    if not objects:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('genres_not_found'))
    return objects
