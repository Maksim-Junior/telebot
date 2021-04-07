import asyncio

import aiohttp
import pytest


@pytest.yield_fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop


@pytest.yield_fixture(scope="session")
async def http_session():
    async with aiohttp.ClientSession() as session:
        yield session