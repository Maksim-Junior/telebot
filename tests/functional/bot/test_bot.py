import os

import pytest
from starlette import status
from starlette.testclient import TestClient

from asgi import app

client = TestClient(app
                    )


@pytest.mark.functional
def test_success_local():
    response = client.get("/config/")
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    data = {"bot_token": os.getenv('BOT_TOKEN'), "pythonpath": os.getenv('PYTHONPATH')}
    assert payload == data


@pytest.mark.functional
def test_success_heroku():
    response = client.get("https://telebotek.herokuapp.com/config/")
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    data = {"bot_token": os.getenv('BOT_TOKEN'), "pythonpath": os.getenv('PYTHONPATH')}
    assert payload == data
