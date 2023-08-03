from typing import Awaitable
from vkwave.bots import SimpleLongPollBot, DefaultRouter, BotEvent, AttachmentTypeFilter, TextStartswithFilter, WallPhotoUploader
from vkwave.api import APIOptionsRequestContext,API
import abstractions
import models
from .dbcontext import DBContext
import dateparser
import re
from datetime import datetime, timedelta
import asyncio
import time
import requests
import io 
from vkwave.client import AIOHTTPClient


class VkSourceBot(abstractions.MemeSource):
    __router: abstractions.AbstractMemeRouter = None


    def __init__(self, **config):
        self.__vk_router = DefaultRouter()
        self.__downloader_long_pool = SimpleLongPollBot(**config["longpool"], router=self.__vk_router)
        self.__vk_router.register_handler(TextStartswithFilter(""), AttachmentTypeFilter(attachment_type="photo") | AttachmentTypeFilter(attachment_type="wall"), callback=self.__schedule_meme)
        self.__vk_router.register_handler(TextStartswithFilter(""), callback=self.__other_message)

        
        
    def set_router(self, router: abstractions.AbstractMemeRouter) -> None:
        self.__router = router

    async def run(self):
        await self.__downloader_long_pool.run()

    async def __other_message(self,event:BotEvent):

        return "No attachments found, see help"


    async def __schedule_meme(self, event: BotEvent):
        message = event.object.object.message
        msg_text = message.text.lower() #lower chars
        attachments = message.attachments

        primary_match = re.match(r"((\w)+, ?)*(\w)+( .+)", msg_text)
        if not primary_match or primary_match.group(0) != msg_text:
            print(event)
            return "Invalid input format, see help"
        
        raw_dates = primary_match.group(4)
        raw_targets = msg_text[:len(msg_text) - len(raw_dates)]
        raw_dates = raw_dates[1:] # remove space

        targets = re.split(r", ?", raw_targets)

        meme_urls = VkSourceBot.__eject_meme_urls(attachments)
        splited_dates = re.split(r",\s*", raw_dates)
        meme_dates: list[datetime] = []

        for raw_date in splited_dates:
            date = dateparser.parse(raw_date)
            if not date:
                return f"{raw_date} is invalid date"
            elif date < datetime.now() + timedelta(minutes = 2):
                return f"{date} is in past (should be in future, at least 2 minutes)"
            else:
                meme_dates.append(date)
        
        memes = map(lambda x: models.Meme(x[0], x[1]), zip(meme_dates, meme_urls))

        return "Send finished:\n" + await self.__router.route_memes(message.from_id, targets, memes)


    @staticmethod
    def __eject_meme_urls(attachments) -> list[str]:
        def get_max_size(photo):
            return sorted(photo.sizes, key = lambda x: x.width * x.height)[-1].url

        photos = filter(lambda x: x.type.value == 'photo', attachments)
        result = list(map(lambda x: get_max_size(x.photo), photos))

        walls = filter(lambda x: x.type.value == 'wall', attachments)
        
        for wall_photo_urls in map(lambda x: VkSourceBot.__eject_meme_urls(x.wall.attachments), walls):
            result += wall_photo_urls

        return result



class VkIntakeBot(abstractions.MemeIntake):
    def __init__(self, token:str, db:DBContext):
        api = API(tokens=token,clients=AIOHTTPClient())
        api_context = api.get_context()
        self.__api = api_context
        self.__uploader = WallPhotoUploader(api_context)
        self.__db = db

    @staticmethod
    def __download(link:str)->io.BytesIO:
        file = io.BytesIO(requests.get(link).content)
        file.seek(0)
        return file

    async def upload_meme(self, sender_id:int, meme:models.Meme):

        async def upload_photo(group_id, photo_link) -> Awaitable[None]:
            photo = VkIntakeBot.__download(photo_link)
            return await self.__uploader.get_attachment_from_io(photo, group_id,"jpg")
        
        user = await self.__db.get_user(sender_id)
        photo_link = await upload_photo(user.group_id, meme.url)
        await self.__api.wall.post(owner_id =  user.group_id, attachments = photo_link, publish_date = time.mktime(meme.datetime.timetuple()))

    async def validate_user(self, sender_id: int) -> Awaitable[str | None]:
        users = await self.__db.get_users() 
        if sender_id not in users:
            return "You are not availible to post, contact Admin"
        else:
            return None

    async def validate_upload(self, sender_id: int, meme: models.Meme) -> Awaitable[str | None]:
        return None
    