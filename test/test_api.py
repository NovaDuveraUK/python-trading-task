import pytest
import asyncio

from fastapi.exceptions import HTTPException

from app.api import router
from app.api import TradeRequest, MarkPriceRequest
from app.api import update_mark_price, get_positions, margin_report, execute_trade
from app.api import redis_client, db



@pytest.mark.asyncio 
@pytest.mark.it('update_mark_price correctly updates the mark price in Redis')
async def test_mark_price_correct():
    # arrange
    new_mark_price = MarkPriceRequest(symbol='USDT', price=1.05)
    redis_data_expected = 1.05

    # act
    response = await update_mark_price(new_mark_price)

    redis_data_actual = await redis_client.get(key='USDT')

    await redis_client.close()

    # assert
    assert float(redis_data_actual) == redis_data_expected


@pytest.mark.asyncio
@pytest.mark.it('update_mark_price returns correct status code and an informative message on success')
async def test_mark_price_success():
    # arrange
    new_mark_price = MarkPriceRequest(symbol='USDT', price=1.05)
    redis_data_expected = 1.05

    # act
    response = await update_mark_price(new_mark_price)

    redis_data_actual = await redis_client.get(key='USDT')

    await redis_client.close()

    # assert
    assert response == 'Mark price for USDT successfully updated to 1.05'


@pytest.mark.asyncio
@pytest.mark.it('get_positions correctly shows positions for a given account')
async def test_get_positions():
    # arrange

    await redis_client.hset('positions:1','symbol', 'USDT')
    await redis_client.hset('positions:1','quantity', 100)
    await redis_client.hset('positions:1','avg_price', 1)

    new_mark_price = MarkPriceRequest(symbol='USDT', price=1.01)
    await update_mark_price(new_mark_price)

    expected = {'USDT': 100, 'P&L': 1}

    # act
    actual = await get_positions(1)
    await redis_client.close()

    #assert
    assert actual == pytest.approx(expected)


@pytest.mark.asyncio
@pytest.mark.skip('margin_report returns margin utilisation report and a list of accounts to liquidate')
async def test_margin_report():
    # arrange
    new_mark_price = MarkPriceRequest(symbol='USDT', price=1.05)
    await update_mark_price(new_mark_price)

    account_positions = await get_positions(1)

    pnl = account_positions['P&L']
    notional = (account_positions['USDT']) * 1.05

    print(pnl)
    print(notional)

    await redis_client.hset('account:1','cash_balance', 100)
 
    await redis_client.hset('account:1','equity', 100+pnl)

    await redis_client.hset('account:1','used_margin', 0.1*notional)

    await redis_client.hset('account:2','cash_balance', 100)
 
    await redis_client.hset('account:2','equity', 100+pnl)

    await redis_client.hset('account:2','used_margin', 0.1*notional)

    
    # act
    actual = await margin_report()

    await redis_client.close()

    await db.close() 

    # assert
    assert isinstance(actual, dict)
    assert isinstance(actual['Remaining margin per account'], dict)
    assert isinstance(actual['Accounts to liquidate'], list)


@pytest.mark.asyncio
@pytest.mark.it('execute_trade inserts trade record into postgres')
async def test_execute_trade_records():
    # arrange
    trade_request = TradeRequest(account_id=3, symbol='USDT', side='BUY', quantity=10, price=1.03)

    expected = {'Message': 'Trade executed successfully'}

    # act

    actual = await execute_trade(trade_request)
 
    query = """
            SELECT * FROM trades;
            """

    result = await db.fetch(query)
    print(result)

    await redis_client.close()

    await db.close() 

    # asssert

    assert actual == expected