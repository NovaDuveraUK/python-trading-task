from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from pydantic.main import BaseModel

import asyncio

from app.redis_helper import RedisClient

router = APIRouter()

redis_client = RedisClient()


# ----------------------------
# Request Models
# ----------------------------
class TradeRequest(BaseModel):
    account_id: int
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    price: float


class MarkPriceRequest(BaseModel):
    symbol: str
    price: float


# ----------------------------
# API Endpoints
# ----------------------------

@router.post("/trade")
async def execute_trade(req: TradeRequest):
    """
    Executes trade:
    - Perform pre-trade margin check using Redis
    - Update positions and balances in Redis
    - Insert trade record into Postgres
    """
    # TODO: implement pre-trade checks, margin logic, position updates
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/positions/{account_id}")
async def get_positions(account_id: int):
    """
    Returns positions & P&L for the account from Redis.
    P&L is based on latest mark prices from Redis.
    """
    # TODO: fetch positions from Redis, calculate P&L
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/mark-price", status_code=201)
async def update_mark_price(req: MarkPriceRequest):
    """
    Updates mark price for a symbol in Redis.
    """
    try:
        await redis_client.set(key=req.symbol, value=req.price)

        return f'Mark price for {req.symbol} successfully updated to {float(req.price)}'

    except Exception:
        raise HTTPException(status_code=501, detail="Not implemented")
    
    finally:
        await redis_client.close()


@router.get("/margin-report")
async def margin_report():
    """
    Returns margin utilisation for all accounts from Redis
    and a list of liquidation candidates.
    """
    # TODO: calculate margin utilisation, find liquidation candidates
    raise HTTPException(status_code=501, detail="Not implemented")
