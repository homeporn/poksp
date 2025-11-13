from sqlmodel import Session, SQLModel, create_engine

from app import crud
from app.models import PlayerCreate, TransactionCreate, TransactionType


def get_memory_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_player_balance_calculation() -> None:
    with get_memory_session() as session:
        player = crud.create_player(session, PlayerCreate(name="Alice"))
        crud.create_transaction(
            session,
            TransactionCreate(
                player_id=player.id,
                amount=100,
                type=TransactionType.BUY_IN,
            ),
        )
        crud.create_transaction(
            session,
            TransactionCreate(
                player_id=player.id,
                amount=250,
                type=TransactionType.WIN,
            ),
        )
        crud.create_transaction(
            session,
            TransactionCreate(
                player_id=player.id,
                amount=50,
                type=TransactionType.LOSS,
            ),
        )

        players = crud.list_players(session)
        assert len(players) == 1
        stats = players[0]
        assert stats.buy_ins_total == 100
        assert stats.winnings_total == 250
        assert stats.losses_total == 50
        assert stats.balance == 100
