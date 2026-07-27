from datetime import datetime
from enum import StrEnum
from typing import Annotated

from fastapi.params import Query
from pydantic import BaseModel, Field


class FileNamesResponse(BaseModel):
    names: list[str] = Field(
        default_factory=list,
        description='Список имён файлов для скачивания',
    )

    model_config = {
        'json_schema_extra': {
            'example': {'names': ['file1.txt', 'file2.txt', 'file3.txt']}
        }
    }


class DownloadRequest(BaseModel):
    names: list[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description='Имена файлов для скачивания (максимум 3)',
    )

    model_config = {
        'json_schema_extra': {'example': {'names': ['file1.txt', 'file2.txt']}}
    }


class MarkDownloadedRequest(BaseModel):
    names: list[str] = Field(
        ...,
        min_length=1,
        description='Имена файлов для отметки как скачанных',
    )

    model_config = {
        'json_schema_extra': {'example': {'names': ['file1.txt', 'file2.txt']}}
    }


class MarkDownloadedResponse(BaseModel):
    marked: int = Field(
        ...,
        ge=0,
        description='Количество файлов, отмеченных как скачанные в этот раз',
    )
    already_marked: int = Field(
        ...,
        ge=0,
        description='Количество файлов, которые уже были отмечены ранее',
    )

    model_config = {
        'json_schema_extra': {'example': {'marked': 2, 'already_marked': 1}}
    }


class ResetResponse(BaseModel):
    reset: bool


class ErrorResponse(BaseModel):
    detail: str = Field(..., description='Описание ошибки')


class NumberStatsResponse(BaseModel):
    number: int
    count: int


class FileResponse(BaseModel):
    id: int
    name: str
    downloaded_at: datetime
    stats: list[NumberStatsResponse] | None = None


class FileListResponse(BaseModel):
    files: list[FileResponse] = Field(default_factory=list)
    stats: list[NumberStatsResponse] | None
    total: int
    pages: int
    first_file_downloaded_at: datetime | None


class FileSorting(StrEnum):
    DOWNLOADED_AT = 'downloaded_at'


class SortingOrder(StrEnum):
    ASC = 'ASC'
    DESC = 'DESC'


class GetDownloadedFilesRequest(BaseModel):
    page: int = 1
    sorting: FileSorting | None = None
    order: SortingOrder = SortingOrder.DESC
    with_stats: Annotated[list[int] | bool, Query(alias='withStats')] = False
