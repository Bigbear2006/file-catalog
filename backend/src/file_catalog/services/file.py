import io
import math
import os
import random
import string
import zipfile

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from file_catalog.config import Config
from file_catalog.exceptions import FileNotFound
from file_catalog.models import DownloadedFile, File
from file_catalog.schemas import (
    FileListResponse,
    FileNamesResponse,
    FileResponse,
    FileSorting,
    MarkDownloadedResponse,
    NumberStatsResponse,
    SortingOrder,
)
from file_catalog.services.candidate import CandidateService

PAGE_SIZE = 5


class FileService:
    def __init__(
        self,
        session: AsyncSession,
        candidate_service: CandidateService,
        config: Config,
    ) -> None:
        self.session = session
        self.candidate_service = candidate_service
        self.config = config

    async def create_or_update_files(self) -> None:
        files = []

        for filename in os.listdir(self.config.FILES_DIR):
            full_path = os.path.join(self.config.FILES_DIR, filename)

            if not os.path.isfile(full_path):
                continue

            with open(full_path, encoding='utf-8') as f:
                content = f.read()

            size = os.path.getsize(full_path)
            files.append({'name': filename, 'content': content, 'size': size})

        if not files:
            return

        stmt = insert(File).values(files)
        stmt = stmt.on_conflict_do_update(
            index_elements=[File.name],
            set_={
                'content': stmt.excluded.content,
                'size': stmt.excluded.size,
            },
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def get_random_files(
        self, min_count: int = 3, max_count: int = 9
    ) -> FileNamesResponse:
        candidate_id = await self.candidate_service.get_current_candidate_id()

        downloaded_stmt = select(DownloadedFile.file_id).where(
            DownloadedFile.candidate_id == candidate_id
        )
        downloaded_result = await self.session.execute(downloaded_stmt)
        downloaded_ids = {row[0] for row in downloaded_result.fetchall()}

        if downloaded_ids:
            stmt = select(File.id, File.name).where(
                ~File.id.in_(downloaded_ids)
            )
        else:
            stmt = select(File.id, File.name)

        result = await self.session.execute(stmt)
        available_files = result.fetchall()

        if not available_files:
            return FileNamesResponse()

        count = min(random.randint(min_count, max_count), len(available_files))
        selected = random.sample(available_files, count)

        return FileNamesResponse(names=[file.name for file in selected])

    async def get_files_by_names(self, names: list[str]) -> list[File]:
        stmt = select(File).where(File.name.in_(names))
        result = await self.session.execute(stmt)
        files = result.scalars().all()

        found_names = {f.name for f in files}
        missing = set(names) - found_names
        if missing:
            raise FileNotFound(missing.pop())

        return list(files)

    async def create_zip_archive(self, files: list[File]) -> bytes:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer, 'w', zipfile.ZIP_DEFLATED
        ) as zip_file:
            for file in files:
                file_path = self.config.FILES_DIR / file.name
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        zip_file.writestr(file.name, f.read())
                else:
                    zip_file.writestr(file.name, file.content)

        zip_buffer.seek(0)
        return zip_buffer.read()

    async def get_downloaded_files(
        self,
        *,
        page: int = 1,
        sorting: FileSorting | None = None,
        order: SortingOrder = SortingOrder.DESC,
        with_stats: list[int] | bool = False,
    ) -> FileListResponse:
        candidate_id = await self.candidate_service.get_current_candidate_id()

        total_stmt = (
            select(func.count('*'))
            .select_from(DownloadedFile)
            .where(DownloadedFile.candidate_id == candidate_id)
        )
        total_result = await self.session.execute(total_stmt)
        total_count = total_result.scalar() or 0

        first_download_stmt = select(func.min(DownloadedFile.downloaded_at))
        first_file_downloaded_at = await self.session.scalar(
            first_download_stmt
        )

        offset = (page - 1) * PAGE_SIZE
        limit = offset + PAGE_SIZE
        stmt = (
            select(DownloadedFile)
            .options(joinedload(DownloadedFile.file))
            .where(DownloadedFile.candidate_id == candidate_id)
            .offset(offset)
            .limit(limit)
        )

        if sorting == FileSorting.DOWNLOADED_AT:
            col = DownloadedFile.downloaded_at
            order_by = col.asc() if order == SortingOrder.ASC else col.desc()
            stmt = stmt.order_by(order_by)

        result = await self.session.execute(stmt)
        files = result.scalars().all()

        stats_by_file_id = {}
        general_stats = None
        if with_stats:
            stats_by_file_id = {
                f.id: [
                    NumberStatsResponse(
                        number=int(number), count=f.file.content.count(number)
                    )
                    for number in string.digits
                ]
                for f in files
                if isinstance(with_stats, bool) or f.file.id in with_stats
            }

            general_stats_dict = {}  # {number: count}
            for stats in stats_by_file_id.values():
                for stat in stats:
                    general_stats_dict.setdefault(stat.number, 0)
                    general_stats_dict[stat.number] += stat.count

            general_stats = [
                NumberStatsResponse(number=number, count=count)
                for number, count in general_stats_dict.items()
            ]

        file_list = [
            FileResponse(
                id=f.file.id,
                name=f.file.name,
                downloaded_at=f.downloaded_at,
                stats=stats_by_file_id.get(f.id),
            )
            for f in files
        ]
        return FileListResponse(
            files=file_list,
            total=total_count,
            pages=math.ceil(total_count / PAGE_SIZE),
            first_file_downloaded_at=first_file_downloaded_at,
            stats=general_stats,
        )

    async def mark_downloaded_files(
        self, names: list[str]
    ) -> MarkDownloadedResponse:
        candidate_id = await self.candidate_service.get_current_candidate_id()

        result = await self.session.scalars(
            select(DownloadedFile)
            .join(File)
            .where(File.name.in_(names))
            .options(contains_eager(DownloadedFile.file))
        )
        already_downloaded = result.all()
        already_downloaded_names = [i.file.name for i in already_downloaded]

        result2 = await self.session.scalars(
            select(File).where(File.name.in_(names))
        )
        file_id_by_name = {file.name: file.id for file in result2.all()}

        new = [
            DownloadedFile(
                candidate_id=candidate_id, file_id=file_id_by_name[name]
            )
            for name in names
            if name not in already_downloaded_names
        ]

        self.session.add_all(new)
        await self.session.commit()
        return MarkDownloadedResponse(
            marked=len(new), already_marked=len(already_downloaded)
        )
