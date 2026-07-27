from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from file_catalog.models import Candidate, DownloadedFile


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def reset_candidate_progress(self, identifier: str) -> bool:
        stmt = select(Candidate).where(
            (Candidate.identifier == identifier)
            | (Candidate.ip_address == identifier)
        )
        result = await self.session.execute(stmt)
        candidate = result.scalar_one_or_none()
        if not candidate:
            return False

        await self.session.execute(
            delete(DownloadedFile).where(
                DownloadedFile.candidate_id == candidate.id
            )
        )

        candidate.request_count = 0
        candidate.blocked_until = None
        candidate.last_request_at = None
        await self.session.commit()
        return True

    async def unblock_client(self, ip_address: str) -> bool:
        stmt = select(Candidate).where(Candidate.ip_address == ip_address)
        result = await self.session.execute(stmt)
        candidate = result.scalar_one_or_none()
        if not candidate:
            return False

        candidate.blocked_until = None
        candidate.request_count = 0
        await self.session.commit()
        return True
