from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class TransactionType(str, Enum):
    BUY_IN = "buy_in"
    WIN = "win"
    LOSS = "loss"


class PlayerBase(SQLModel):
    name: str = Field(index=True)
    telegram_username: Optional[str] = Field(default=None, index=True)


class Player(PlayerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: list[Transaction] = Relationship(back_populates="player")


class PlayerCreate(PlayerBase):
    ...


class PlayerRead(PlayerBase):
    id: int
    buy_ins_total: float
    winnings_total: float
    losses_total: float
    balance: float


class TransactionBase(SQLModel):
    amount: float = Field(gt=0)
    note: Optional[str] = None


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    type: TransactionType = Field(sa_column_kwargs={"nullable": False})
    player_id: int = Field(foreign_key="player.id")
    player: Optional[Player] = Relationship(back_populates="transactions")


class TransactionCreate(TransactionBase):
    type: TransactionType
    player_id: int


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    type: TransactionType
    player_id: int
