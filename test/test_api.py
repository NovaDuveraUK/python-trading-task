import pytest
import asyncio

from fastapi.exceptions import HTTPException

from app.api import router
from app.api import TradeRequest, MarkPriceRequest
from app.api import update_mark_price, get_positions
from app.api import redis_client



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


