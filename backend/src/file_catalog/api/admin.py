from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Header, HTTPException, Path
from starlette import status

from file_catalog.config import Config
from file_catalog.di.container import container
from file_catalog.schemas import ErrorResponse, ResetResponse
from file_catalog.services import AdminService


def check_admin_token(
    x_admin_token: Annotated[str | None, Header(alias='X-Admin-Token')] = None,
) -> None:
    config = container.get_sync(Config)
    if x_admin_token != config.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Неверный или отсутствующий токен администратора',
        )


admin_router = APIRouter(
    prefix='/admin',
    tags=['Администрирование'],
    dependencies=[Depends(check_admin_token)],
    route_class=DishkaRoute,
)


@admin_router.delete(
    '/candidates/{candidate_id}/progress',
    summary='Сбросить прогресс скачивания кандидата',
    responses={403: {'model': ErrorResponse}},
)
async def reset_candidate_progress(
    candidate_id: Annotated[str, Path()],  # X-Candidate-Id or IP
    admin_service: FromDishka[AdminService],
) -> ResetResponse:
    """Удалить отметки о скачанных файлах — кандидат сможет начать заново."""
    success = await admin_service.reset_candidate_progress(candidate_id)
    return ResetResponse(reset=success)


@admin_router.delete(
    '/clients/{client_ip}/throttling',
    summary='Снять бан и обнулить счётчики частоты запросов',
    responses={403: {'model': ErrorResponse}},
)
async def unblock_client(
    client_ip: Annotated[str, Path()],
    admin_service: FromDishka[AdminService],
) -> ResetResponse:
    """Досрочно разблокировать клиента и очистить его счётчики нарушений."""
    success = await admin_service.unblock_client(client_ip)
    return ResetResponse(reset=success)
