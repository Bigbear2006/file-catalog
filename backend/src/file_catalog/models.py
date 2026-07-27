from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class File(Base):
    __tablename__ = 'files'

    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    downloads: Mapped[list['DownloadedFile']] = relationship(
        'DownloadedFile',
        back_populates='file',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f'<File(id={self.id}, name={self.name}, size={self.size})>'


class Candidate(Base):
    __tablename__ = 'candidates'

    # X-Candidate-Id
    identifier: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    blocked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    request_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_request_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    downloads: Mapped[list['DownloadedFile']] = relationship(
        'DownloadedFile',
        back_populates='candidate',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return (
            f'<Candidate(id={self.id}, identifier={self.identifier}, '
            f'ip_address={self.ip_address})>'
        )


class DownloadedFile(Base):
    __tablename__ = 'downloaded_files'

    candidate_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('candidates.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    file_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('files.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    candidate: Mapped['Candidate'] = relationship(
        'Candidate', back_populates='downloads'
    )
    file: Mapped['File'] = relationship('File', back_populates='downloads')

    __table_args__ = (
        UniqueConstraint('candidate_id', 'file_id', name='uq_candidate_file'),
    )

    def __repr__(self) -> str:
        return (
            f'<DownloadedFile(candidate_id={self.candidate_id}, '
            f'file_id={self.file_id})>'
        )
