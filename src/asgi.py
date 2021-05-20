import enum

import asyncpg
from typing import Optional
from urllib.parse import parse_qs

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, Path
from pydantic import Field
from pydantic.main import BaseModel
from starlette.requests import Request
from starlette.responses import HTMLResponse

import telegram
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


@enum.unique
class UserStatus(enum.Enum):
    INITIAL = 1
    WAITING_FOR_USERNAME = 2
    WAITING_FOR_PASSWORD = 3


@app.post("/webhook/")
async def handle_webhook(update: telegram.Update):
    debug(update)
    try:
        user: User2 = await get_or_create_user(update.message.from_.id)
        if user.blog_user_id:
            await telegram.send_message(
                chat_id=update.message.chat.id,
                reply_to_message_id=update.message.message_id,
                text=f"ТЫ: {user}, пишешь какую-то дичь: {update.message.text}",
            )
        else:
            if user.status == UserStatus.INITIAL.value:
                await ask_for_username(update.message.chat.id)
            elif user.status == UserStatus.WAITING_FOR_USERNAME.value:
                await setup_username(update.message.from_.id, update.message.text)
                await ask_for_password(update.message.chat.id)
            elif user.status == UserStatus.WAITING_FOR_PASSWORD.value:
                password = update.message.text
                await auth_on_blog(user.blog_username, password)
            else:
                raise RuntimeError(f"unknown status: {user.status}")

    except Exception as err:  # pylint: disable=broad-except
        import traceback  # pylint: disable=import-outside-toplevel

        debug(err)
        debug(traceback.format_exc())

    return {"ok": True}


async def response_to_tg(chat_id: int, text: str, photo: str):
    reply = MessageReply(
        chat_id=chat_id,
        text=text,
        photo=photo,
    )
    if photo:
        async with aiohttp.ClientSession() as sesss:
            url = f"https://api.telegram.org/bot{settings.bot_token}/sendPhoto"
            async with sesss.post(url, json=reply.dict()) as resp:
                payload = await resp.json()
                debug(payload)
                debug(resp)
    else:
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
        data = {"url": f"https://f7137eb96d1f.ngrok.io/webhook/"}
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


class User2(BaseModel):
    id: int
    user_id: int
    blog_user_id: Optional[int] = Field(None)
    blog_username: Optional[str] = Field(None)
    status: int = Field(...)


@app.post("/xxx/{user_id}/")
async def xxx(user_id: int = Path(...)):
    conn = await asyncpg.connect(dsn=settings.database_url)
    try:
        values = await conn.fetch(
            'select * from users where id = $1;',
            user_id,
        )
        debug(values)
        values2 = [
            User2.parse_obj(obj)
            for obj in values
        ]
        return values2
    finally:
        await conn.close()
