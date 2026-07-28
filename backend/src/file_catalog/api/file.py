from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, Response

from file_catalog.schemas import (
    DownloadRequest,
    ErrorResponse,
    FileListResponse,
    FileNamesResponse,
    GetDownloadedFilesRequest,
    MarkDownloadedRequest,
    MarkDownloadedResponse,
)
from file_catalog.services import FileService

file_router = APIRouter(
    prefix='/files', tags=['Файлы'], route_class=DishkaRoute
)


@file_router.get(
    '/names',
    summary='Получить случайные имена файлов для скачивания',
    responses={403: {'model': ErrorResponse}, 429: {'model': ErrorResponse}},
)
async def get_random_file_names(
    file_service: FromDishka[FileService],
) -> FileNamesResponse:
    """Выдать случайную порцию имён файлов,
    ещё не отмеченных кандидатом как скачанные.
    Размер порции случаен (от 3 до 9 имён).
    Когда неотмеченных файлов меньше размера порции, вернутся все оставшиеся;
    когда каталог скачан полностью — пустой список.
    Общее количество файлов сервис не раскрывает."""

    return await file_service.get_random_files()


@file_router.post(
    '/download',
    summary='Скачать файлы по именам',
    responses={
        200: {'content': {'application/zip': {}}},
        403: {'model': ErrorResponse},
        404: {'model': ErrorResponse},
        429: {'model': ErrorResponse},
    },
)
async def download_files(
    data: DownloadRequest, file_service: FromDishka[FileService]
) -> Response:
    """Отдать запрошенные файлы одним ZIP-архивом.

    За один запрос можно получить не более 3 файлов —
    скачивание «всего и сразу» намеренно невозможно.
    Скачивание не отмечает файлы как полученные:
    об этом нужно отдельно сообщить ручкой `POST /api/files/downloaded`."""

    files = await file_service.get_files_by_names(data.names)

    zip_content = await file_service.create_zip_archive(files)
    return Response(
        content=zip_content,
        media_type='application/zip',
        headers={
            'Content-Disposition': 'attachment; filename="files.zip"',
            'Content-Length': str(len(zip_content)),
        },
    )


@file_router.get('/downloaded')
async def get_downloaded_files(
    data: Annotated[GetDownloadedFilesRequest, Query()],
    file_service: FromDishka[FileService],
) -> FileListResponse:
    if data.with_stats and isinstance(data.with_stats[0], bool):
        with_stats = data.with_stats[0]
    else:
        with_stats = data.with_stats  # type: ignore[assignment]

    return await file_service.get_downloaded_files(
        page=data.page,
        sorting=data.sorting,
        order=data.order,
        with_stats=with_stats,
    )


@file_router.post(
    '/downloaded',
    response_model=MarkDownloadedResponse,
    summary='Отметить файлы как скачанные',
    responses={
        403: {'model': ErrorResponse},
        429: {'model': ErrorResponse},
    },
)
async def mark_files_downloaded(
    data: MarkDownloadedRequest, file_service: FromDishka[FileService]
) -> MarkDownloadedResponse:
    """Зафиксировать, что кандидат скачал перечисленные файлы.

    Отмеченные файлы больше не попадают в выдачу ручки
    `GET /api/files/names` для этого кандидата.
    Повторная отметка не является ошибкой
    и учитывается в поле already_marked"""

    return await file_service.mark_downloaded_files(data.names)
