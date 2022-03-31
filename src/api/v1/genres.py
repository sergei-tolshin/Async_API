from http import HTTPStatus
from typing import Optional

from core.paginator import Paginator
from core.utils.translation import gettext_lazy as _
from fastapi import APIRouter, Depends, HTTPException, Request
from models.genre import GenreDetailsResponseModel, GenrePagination
from services.genres import GenreService, get_genre_service

from .utils.genres import Sort

router = APIRouter()


@router.get('/{genre_id}',
            response_model=GenreDetailsResponseModel,
            summary='Подробная информация о жанре',
            description='Вывод подробной информации о жанре',
            response_description='uuid, название, описание',
            tags=['Жанры']
            )
async def details(
    request: Request,
    genre_id: str,
    service: GenreService = Depends(get_genre_service)
) -> GenreDetailsResponseModel:
    service.data_manager.request = request
    obj = await service.retrieve(genre_id)
    if not obj:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('genre_not_found'))
    return obj


@router.get('/',
            response_model=GenrePagination,
            summary='Список жанров',
            description=("Список жанров с постраничным разбиением "
                         "и сортировкой по названию"),
            response_description='uuid, название',
            tags=['Жанры']
            )
async def list(
    request: Request,
    service: GenreService = Depends(get_genre_service),
    sort: Sort = Depends(),
    paginator: Paginator = Depends(),
) -> GenrePagination:
    params: dict = {
        'page[size]': paginator.page_size,
        'page[number]': paginator.page_number,
        'sort': sort.sort,
    }
    service.request = request
    service.paginator = paginator
    objects: Optional[dict] = await service.list(params)
    if not objects:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=_('genres_not_found'))
    return objects
