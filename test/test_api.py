import pytest
import asyncio

from fastapi.exceptions import HTTPException

from app.api import router
from app.api import TradeRequest, MarkPriceRequest
from app.api import update_mark_price
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




