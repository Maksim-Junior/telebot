import pytest
from dotenv import load_dotenv
from starlette import status

from config import settings

load_dotenv()


@pytest.mark.asyncio
async def test(http_session):
    service = settings.service_url
    assert service

    url_settings = f"{service}/settings/"

    async with http_session.get(url_settings) as resp:
        assert resp.status == status.HTTP_200_OK

        payload = await resp.json()

        bot_token = payload.get("bot_token")
        assert bot_token == settings.bot_token
