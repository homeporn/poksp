from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from . import crud
from .database import create_db_and_tables, engine, get_session
from .models import PlayerCreate, TransactionCreate, TransactionType

app = FastAPI(title="Poker Stack - Telegram Mini App Backend")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.on_event("shutdown")
def on_shutdown() -> None:
    engine.dispose()


def get_db() -> Session:
    with get_session() as session:
        yield session


@app.get("/", response_class=HTMLResponse)
def read_dashboard(request: Request, session: Session = Depends(get_db)) -> HTMLResponse:
    players = crud.list_players(session)
    transactions = crud.list_transactions(session)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "players": players,
            "transactions": transactions,
            "transaction_types": TransactionType,
        },
    )


@app.post("/players", response_class=HTMLResponse)
def create_player(
    request: Request,
    name: str = Form(...),
    telegram_username: str | None = Form(default=None),
    session: Session = Depends(get_db),
) -> HTMLResponse:
    player_in = PlayerCreate(name=name, telegram_username=telegram_username or None)
    crud.create_player(session, player_in)
    url = request.url_for("read_dashboard")
    return RedirectResponse(url, status_code=303)


@app.post("/transactions", response_class=HTMLResponse)
def create_transaction(
    request: Request,
    player_id: int = Form(...),
    amount: float = Form(...),
    type: str = Form(...),
    note: str | None = Form(default=None),
    session: Session = Depends(get_db),
) -> HTMLResponse:
    try:
        tx_type = TransactionType(type)
    except ValueError as exc:  # pragma: no cover - form validation
        raise HTTPException(status_code=400, detail="Invalid transaction type") from exc

    tx_in = TransactionCreate(
        player_id=player_id,
        amount=amount,
        type=tx_type,
        note=note or None,
    )
    crud.create_transaction(session, tx_in)
    url = request.url_for("read_dashboard")
    return RedirectResponse(url, status_code=303)
