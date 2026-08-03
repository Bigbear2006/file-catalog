from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

from environs import env

env.read_env()


@dataclass
class Config:
    POSTGRES_DB: str = field(default_factory=lambda: env('POSTGRES_DB'))
    POSTGRES_HOST: str = field(default_factory=lambda: env('POSTGRES_HOST'))
    POSTGRES_PORT: int = field(
        default_factory=lambda: env.int('POSTGRES_PORT')
    )
    POSTGRES_USER: str = field(default_factory=lambda: env('POSTGRES_USER'))
    POSTGRES_PASSWORD: str = field(
        default_factory=lambda: env('POSTGRES_PASSWORD')
    )

    FILES_DIR: Path = field(default_factory=lambda: env.path('FILES_DIR'))
    ADMIN_TOKEN: str = field(default_factory=lambda: env('ADMIN_TOKEN'))

    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 5
    BLOCK_DURATION_SECONDS: int = 1800

    TZ: ZoneInfo = field(default_factory=lambda: ZoneInfo('Asia/Novosibirsk'))

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
