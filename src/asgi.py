import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import Field
from pydantic.main import BaseModel

from config import settings
from util import debug

app = FastAPI()

load_dotenv()


class ConfigParams(BaseModel):
    bot_token: Optional[str] = Field(None)
    pythonpath: Optional[str] = Field(None)


@app.get("/settings/")
async def handle_settings():
    debug(settings)
    return settings
