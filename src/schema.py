from typing import Optional

from pydantic import BaseModel, Field


class Chat(BaseModel):
    id: int


class Message(BaseModel):
    message_id: int
    chat: Chat
    date: int
    text: Optional[str] = Field(None, min_length=0, max_length=2 ** 12)
    from_: Optional[str] = Field(None, min_length=0, max_length=2 ** 12)
    reply_to_message: Optional["Message"] = Field(None)


class Update(BaseModel):
    update_id: int
    message: Message


class MessageReply(BaseModel):
    chat_id: int
    text: str
    photo: str = None
