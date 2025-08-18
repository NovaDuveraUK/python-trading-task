from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from pydantic.main import BaseModel

import asyncio
from datetime import datetime

from app.redis_helper import RedisClient
from app.postgres import AsyncPostgresClient

router = APIRouter()

redis_client = RedisClient()


# change the user ad password to your own credentials
db = AsyncPostgresClient(user='user', password='password',database='trading_system')


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

    try:
        
        # checks for pre-trade margin goes here

        # if not enough margin - message 'unsuccessful'

        # if enough margin - proceed with the steps below

        # updating redis balances goes here


        query = f"""
            INSERT INTO trades
                (account_id, symbol, side, quantity, price, time_stamp)
            VALUES
                ({req.account_id}, '{req.symbol}', '{req.side}', {req.quantity}, {req.price}, '{datetime.now()}');
                """
        
        await db.execute(query)

        return {'Message': 'Trade executed successfully'}

    except Exception:
        raise HTTPException(status_code=501, detail="Not implemented")
    
    finally:
        await redis_client.close()
        await db.close() 


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
    try:
        query = """
                SELECT DISTINCT account_id FROM trades;
                """
        
        account_ids = await db.fetch(query)

        accounts = []

        for id in account_ids:
            accounts.append(id['account_id'])

        remaining_margin_per_acc = {}

        for account in accounts:

            account_status_bytes = await redis_client.hgetall(f'account:{account}')

            account_status = {}

            for key in account_status_bytes:
                account_status[key.decode('utf-8')] = account_status_bytes[key].decode('utf-8')

            equity = float(account_status['equity'])
            used_margin = float(account_status['used_margin'])

            remaining_margin_per_acc[account] = equity - used_margin

        accounts_to_liquidate = []

        for account in remaining_margin_per_acc:
            if remaining_margin_per_acc[account] < 0:
                accounts_to_liquidate.append(account)


        return {'Remaining margin per account': remaining_margin_per_acc, 'Accounts to liquidate': accounts_to_liquidate}


    except Exception:
        raise HTTPException(status_code=501, detail="Not implemented")
    
    finally:
        await redis_client.close()
        await db.close()    



    
    
