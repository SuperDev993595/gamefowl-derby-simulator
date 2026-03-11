from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class TournamentStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    FINISHED = "finished"


class EntryStatus(str, enum.Enum):
    ACTIVE = "active"
    ELIMINATED = "eliminated"


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    PLAYED = "played"
    BYE = "bye"


class DerbyType(str, enum.Enum):
    LONG_HEEL = "long_heel"
    SHORT_HEEL = "short_heel"
    PILIPINO = "pilipino"
    MEXICAN = "mexican"


class KeepType(str, enum.Enum):
    BENCH = "bench"
    FLYPEN = "flypen"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    token_balance: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entries: Mapped[list["Entry"]] = relationship("Entry", back_populates="user")


class Breed(Base):
    __tablename__ = "breeds"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    image_filename: Mapped[str] = mapped_column(String(128), nullable=False)

    traits: Mapped[list["BreedTrait"]] = relationship("BreedTrait", back_populates="breed")


class BreedTrait(Base):
    __tablename__ = "breed_traits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    breed_id: Mapped[int] = mapped_column(ForeignKey("breeds.id"), nullable=False)
    derby_type: Mapped[str] = mapped_column(String(32), nullable=False)
    power: Mapped[int] = mapped_column(Integer, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, nullable=False)
    intelligence: Mapped[int] = mapped_column(Integer, nullable=False)
    stamina: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy: Mapped[int] = mapped_column(Integer, nullable=False)

    breed: Mapped["Breed"] = relationship("Breed", back_populates="traits")


class Tournament(Base):
    __tablename__ = "tournaments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    derby_type: Mapped[str] = mapped_column(String(32), nullable=False)
    total_rounds: Mapped[int] = mapped_column(Integer, nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=TournamentStatus.DRAFT.value)
    current_round: Mapped[int] = mapped_column(Integer, default=0)
    is_tie_breaker: Mapped[bool] = mapped_column(Boolean, default=False)
    winner_entry_id: Mapped[int | None] = mapped_column(ForeignKey("entries.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entries: Mapped[list["Entry"]] = relationship(
        "Entry",
        back_populates="tournament",
        foreign_keys="Entry.tournament_id",
    )
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="tournament")


class Entry(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    breed_id: Mapped[int] = mapped_column(ForeignKey("breeds.id"), nullable=False)
    keep_type: Mapped[str] = mapped_column(String(32), default=KeepType.BENCH.value)
    token_cost_paid: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default=EntryStatus.ACTIVE.value)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="entries")
    tournament: Mapped["Tournament"] = relationship(
        "Tournament",
        back_populates="entries",
        foreign_keys=[tournament_id],
    )
    breed: Mapped["Breed"] = relationship("Breed")


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_a_id: Mapped[int | None] = mapped_column(ForeignKey("entries.id"), nullable=True)
    entry_b_id: Mapped[int | None] = mapped_column(ForeignKey("entries.id"), nullable=True)
    winner_entry_id: Mapped[int | None] = mapped_column(ForeignKey("entries.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=MatchStatus.PENDING.value)
    is_tie_breaker: Mapped[bool] = mapped_column(Boolean, default=False)
    played_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="matches")
