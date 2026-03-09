from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    is_admin: bool = False
    token_balance: int = 0


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    token_balance: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BreedTraitResponse(BaseModel):
    derby_type: str
    power: int
    speed: int
    intelligence: int
    stamina: int
    accuracy: int


class BreedResponse(BaseModel):
    id: int
    name: str
    image_filename: str
    traits: Optional[list[BreedTraitResponse]] = None

    class Config:
        from_attributes = True


class TournamentCreate(BaseModel):
    name: str
    derby_type: str
    total_rounds: int = 10
    start_at: Optional[datetime] = None


class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    derby_type: Optional[str] = None
    total_rounds: Optional[int] = None
    start_at: Optional[datetime] = None


class TournamentResponse(BaseModel):
    id: int
    name: str
    derby_type: str
    total_rounds: int
    start_at: Optional[datetime]
    status: str
    current_round: int
    is_tie_breaker: bool
    winner_entry_id: Optional[int] = None
    created_at: datetime
    entry_count: Optional[int] = None

    class Config:
        from_attributes = True


class EntryCreate(BaseModel):
    breed_id: int


class EntryResponse(BaseModel):
    id: int
    tournament_id: int
    user_id: int
    breed_id: int
    token_cost_paid: int
    status: str
    wins: int
    losses: int
    created_at: datetime
    username: Optional[str] = None
    breed_name: Optional[str] = None

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    tournament_id: int
    round_number: int
    entry_a_id: Optional[int] = None
    entry_b_id: Optional[int] = None
    winner_entry_id: Optional[int] = None
    status: str
    is_tie_breaker: bool
    played_at: Optional[datetime] = None
    entry_a_username: Optional[str] = None
    entry_b_username: Optional[str] = None
    entry_a_breed: Optional[str] = None
    entry_b_breed: Optional[str] = None

    class Config:
        from_attributes = True


class StandingsRow(BaseModel):
    entry_id: int
    username: str
    breed_name: str
    wins: int
    losses: int
    status: str


class WebSocketMessage(BaseModel):
    event: str
    tournament_id: Optional[int] = None
    payload: Optional[dict] = None
