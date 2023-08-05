import abstractions
import models
from .dbcontext import DBContext
import re
from datetime import datetime
import requests
import io 
import aiogram
import asyncio 
from typing import Awaitable


class TelegramIntakeBot(abstractions.MemeIntake):
    def __init__(self, token:str, db:DBContext):
        self.__bot = aiogram.Bot(token = token)
        self.__db = db

    @staticmethod
    def __download(link:str)->io.BytesIO:
        file = io.BytesIO(requests.get(link).content)
        file.seek(0)
        return file

    async def upload_meme(self, sender_id:int, meme:models.Meme):

        user = await self.__db.get_user(sender_id)
        photo = TelegramIntakeBot.__download(meme.url)
        time_delta = meme.datetime-datetime.now()
        await asyncio.sleep(time_delta.total_seconds())
        await self.__bot.send_photo(chat_id=user.group_id,photo=photo)

    async def validate_user(self, sender_id: int):
        users = await self.__db.get_users() 
        if sender_id not in users:
            raise Exception("You are not availible to post, contact Admin")

    async def validate_upload(self, sender_id: int, meme: models.Meme) -> Awaitable[str | None]:
        return None
    