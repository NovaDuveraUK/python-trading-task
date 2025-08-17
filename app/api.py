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

    try:
        positions_bytes = await redis_client.hgetall(f'positions:{account_id}')

        positions = {}

        for key in positions_bytes:
            positions[key.decode('utf-8')] = positions_bytes[key].decode('utf-8')

        positions['quantity'] = float(positions['quantity'])
        positions['avg_price'] = float(positions['avg_price'])

        mark_price = await redis_client.get(key='USDT')
        mark_price = float(mark_price.decode('utf-8'))

        pnl = positions['quantity'] * (mark_price - positions['avg_price'])

        return {'USDT': positions['quantity'], 'P&L': pnl}

    except Exception:
        raise HTTPException(status_code=501, detail="Not implemented")

    finally:
        await redis_client.close()

    


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
