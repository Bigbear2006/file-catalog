import math
from datetime import UTC, datetime, timedelta

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from file_catalog.config import Config
from file_catalog.exceptions import RateLimitExceeded
from file_catalog.logging import logger
from file_catalog.models import Candidate


class CandidateService:
    def __init__(
        self, session: AsyncSession, request: Request, config: Config
    ):
        self.session = session
        self.request = request
        self.config = config

    async def get_candidate(
        self,
        x_candidate_id: str | None = None,
        ip_address: str | None = None,
    ) -> Candidate | None:
        if x_candidate_id:
            stmt = (
                select(Candidate)
                .where(Candidate.identifier == x_candidate_id)
                .with_for_update()
            )
            result = await self.session.execute(stmt)
            candidate = result.scalar_one_or_none()
            if candidate:
                return candidate

        if ip_address:
            stmt = (
                select(Candidate)
                .where(Candidate.ip_address == ip_address)
                .order_by(Candidate.created_at.desc())
                .with_for_update()
                .limit(1)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        return None

    async def get_or_create_candidate(
        self,
        x_candidate_id: str | None = None,
        ip_address: str | None = None,
    ) -> Candidate:
        candidate = await self.get_candidate(x_candidate_id, ip_address)
        if candidate:
            if ip_address and not candidate.ip_address:
                candidate.ip_address = ip_address
                await self.session.commit()
            return candidate

        candidate = Candidate(identifier=x_candidate_id, ip_address=ip_address)
        self.session.add(candidate)
        await self.session.commit()
        logger.info(f'Created candidate {candidate}')

        # Select created candidate with FOR UPDATE lock
        candidate = await self.get_candidate(
            candidate.identifier, candidate.ip_address
        )
        if not candidate:
            raise RuntimeError('Cannot select created candidate')
        return candidate

    def get_client_ip(self) -> str | None:
        logger.info(
            f'Client IP: {self.request.client}\n'
            f'X-Forwarded-For: {self.request.headers.get("X-Forwarded-For")}\n'
            f'X-Real-IP: {self.request.headers.get("X-Real-IP")}\n'
        )

        if forwarded := self.request.headers.get('X-Forwarded-For'):
            return forwarded.split(',')[0].strip()

        if real_ip := self.request.headers.get('X-Real-IP'):
            return real_ip

        if self.request.client:
            return self.request.client.host

        return None

    async def get_current_candidate(self) -> Candidate:
        x_candidate_id = self.request.headers.get('X-Candidate-Id')
        ip_address = self.get_client_ip()
        candidate = await self.get_or_create_candidate(
            x_candidate_id=x_candidate_id,
            ip_address=ip_address,
        )
        await self.check_rate_limit(candidate)
        return candidate

    async def get_current_candidate_id(self) -> int:
        candidate = await self.get_current_candidate()
        return candidate.id

    async def check_rate_limit(self, candidate: Candidate) -> None:
        now = datetime.now(UTC)
        window_start = now - timedelta(
            seconds=self.config.RATE_LIMIT_WINDOW_SECONDS
        )

        if candidate.blocked_until and candidate.blocked_until > now:
            retry_after = math.ceil(
                (candidate.blocked_until - now).total_seconds()
            )
            raise RateLimitExceeded(retry_after=retry_after, blocked=True)

        # Check request count in current window
        if (
            candidate.last_request_at
            and candidate.last_request_at >= window_start
        ):
            # If the candidate exceeds 50% of the request limit,
            # trigger a temporary block to slow down the client
            if candidate.request_count > (
                self.config.RATE_LIMIT_REQUESTS // 2
            ):
                candidate.request_count += 1
                candidate.last_request_at = now
                await self.session.commit()
                raise RateLimitExceeded(
                    retry_after=self.config.RATE_LIMIT_WINDOW_SECONDS,
                )

            if candidate.request_count >= self.config.RATE_LIMIT_REQUESTS:
                candidate.blocked_until = now + timedelta(
                    seconds=self.config.BLOCK_DURATION_SECONDS
                )
                await self.session.commit()
                raise RateLimitExceeded(
                    retry_after=self.config.BLOCK_DURATION_SECONDS,
                    blocked=True,
                )
            candidate.request_count += 1
        else:
            # New window
            candidate.request_count = 1

        candidate.last_request_at = now
        await self.session.commit()
