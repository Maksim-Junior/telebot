import os
from typing import Optional
from urllib.parse import parse_qs

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import Field
from pydantic.main import BaseModel
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config import settings
from schema import Update, MessageReply
from util import debug

app = FastAPI()

load_dotenv()


class ConfigParams(BaseModel):
    bot_token: Optional[str] = Field(None)
    pythonpath: Optional[str] = Field(None)


@app.get("/")
async def main():
    data = await getWebhookInfo()
    if data["url"].startswith("https"):
        text = f"Your WebHook url -> {data['url']}"
    else:
        text = "WebHook not exposed!"

    with open("src/index.html", "r") as abc:
        web = abc.read()
    return HTMLResponse(web.format(show_text=text))


@app.post("/")
async def main_post(request: Request):
    password = await request.body()
    data = parse_qs(password.decode())
    if data:
        word = 0
        for key in data:
            word = key
    else:
        word = 0

    if word == "pass":
        password = data.get("pass", 0)[0]
        if password == settings.password:
            result = await setWebHook()
        else:
            result = "Wrong password!"

    elif word == "pass2":
        password = data.get("pass2", 0)[0]
        if password == settings.password:
            result = await deleteWebHook()
        else:
            result = "Wrong password!"

    else:
        result = "Enter password!"

    with open("src/index.html", "r") as abc:
        web = abc.read()
    return HTMLResponse(web.format(show_text=result))


@app.post("/setWebHook/")
async def setWebHookView(request: Request):
    password = await request.body()
    password = password.decode()
    password = password[1:-1]
    debug(password)
    if password == settings.password:
        text = await setWebHook()
    else:
        text = "Wrong password!"

    return {"result": text}


@app.get("/settings/")
async def handle_settings():
    debug(settings)
    return settings


@app.post("/webhook/")
async def tg_webhook(update: Update):
    try:
        await response_to_tg(
            chat_id=update.message.chat.id,
            text=update.message.text,
        )

    finally:
        return {"ok": True}


async def response_to_tg(chat_id: int, text: str):
    reply = MessageReply(
        chat_id=chat_id,
        text=text
    )
    async with aiohttp.ClientSession() as sesss:
        url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
        async with sesss.post(url, json=reply.dict()) as resp:
            payload = await resp.json()
            debug(payload)
            debug(resp)


async def getWebhookInfo():
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{settings.bot_token}/getWebhookInfo"
        async with session.post(url) as data:
            data = await data.json()
            done_data = dict(data)
            result = done_data["result"]
            debug(result)

            return result


async def setWebHook():
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{settings.bot_token}/setWebHook"
        data = {"url": f"{settings.server_url}/webhook/"}
        async with session.post(url, json=data) as data:
            data = await data.json()
            done_data = dict(data)
            result = done_data["description"]

            info = await getWebhookInfo()
            result = f'{result} {info["url"]}'

            return result


async def deleteWebHook():
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{settings.bot_token}/deleteWebHook"
        async with session.post(url) as data:
            data = await data.json()
            done_data = dict(data)
            result = f'Deleting Webhook: {done_data["result"]}'
            debug(result)

            return result
