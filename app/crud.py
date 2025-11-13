from collections import defaultdict
from typing import Iterable

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .models import (
    Player,
    PlayerCreate,
    PlayerRead,
    Transaction,
    TransactionCreate,
    TransactionType,
)


def create_player(session: Session, player_in: PlayerCreate) -> Player:
    player = Player.model_validate(player_in)
    session.add(player)
    session.commit()
    session.refresh(player)
    return player


def list_players(session: Session) -> list[PlayerRead]:
    players = session.exec(select(Player)).all()
    player_ids = [player.id for player in players]
    if not player_ids:
        return []

    transactions = session.exec(
        select(Transaction)
        .where(Transaction.player_id.in_(player_ids))
        .options(selectinload(Transaction.player))
    ).all()

    grouped: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for tx in transactions:
        grouped[tx.player_id][tx.type] += tx.amount

    results: list[PlayerRead] = []
    for player in players:
        totals = grouped.get(player.id, {})
        buy_ins = totals.get(TransactionType.BUY_IN, 0.0)
        wins = totals.get(TransactionType.WIN, 0.0)
        losses = totals.get(TransactionType.LOSS, 0.0)
        balance = wins - losses - buy_ins
        results.append(
            PlayerRead(
                id=player.id,
                name=player.name,
                telegram_username=player.telegram_username,
                buy_ins_total=round(buy_ins, 2),
                winnings_total=round(wins, 2),
                losses_total=round(losses, 2),
                balance=round(balance, 2),
            )
        )
    return results


def create_transaction(session: Session, tx_in: TransactionCreate) -> Transaction:
    tx = Transaction.model_validate(tx_in)
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx


def list_transactions(session: Session, player_id: int | None = None) -> Iterable[Transaction]:
    statement = (
        select(Transaction)
        .options(selectinload(Transaction.player))
        .order_by(Transaction.created_at.desc())
    )
    if player_id is not None:
        statement = statement.where(Transaction.player_id == player_id)
    return session.exec(statement).all()
