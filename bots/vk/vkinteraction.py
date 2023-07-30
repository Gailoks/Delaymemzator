from vkwave.bots import SimpleLongPollBot, DefaultRouter, BotEvent, AttachmentTypeFilter, TextStartswithFilter
from vkwave.api import API
import abstractions
import models
from . import dbcontext
import dateparser
import re
from datetime import datetime, timedelta
import asyncio

class VkSourceBot(abstractions.MemeSource):
    __router: abstractions.MemeRouter = None


    def __init__(self, **config):
        self.__vk_router = DefaultRouter()
        self.__downloader_long_pool = SimpleLongPollBot(**config["longpool"], router=self.__vk_router)

    def initialize(self):
        self.__vk_router.register_handler(TextStartswithFilter(""), AttachmentTypeFilter(attachment_type="photo"), callback=self.__schedule_meme)
        
    def set_router(self, router: abstractions.MemeRouter) -> None:
        self.__router = router

    async def run(self):
        await self.__downloader_long_pool.run() # TODO: fix

    async def __schedule_meme(self, event: BotEvent):
        message = event.object.object.message
        msg_text = message.text
        attachments = message.attachments

        primary_match = re.match(r"((\w)+, ?)*(\w)+( .+)", msg_text)
        if not primary_match or primary_match.group(0) != msg_text:
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
        status_codes: list[str] = []
        for meme in memes:
            status_codes.append(await self.__router.route_meme(message.from_id, targets, meme))

        return "Send finished: \n" + "\n".join(map(lambda x: f"[{x[0] + 1}]: {x[1]}", enumerate(status_codes)))


    @staticmethod
    def __eject_meme_urls(attachments) -> list[str]:
        return list(map(lambda x: sorted(x.photo.sizes, key = lambda x : x.width * x.height)[-1].url, attachments))



class VkIntakeBot(abstractions.MemeIntake):
    def __init__(self) -> None:
        pass

    async def upload_meme(self, sender_id: int, meme: models.Meme):
        print(f"sender:{sender_id}, datetime:{meme.datetime}, url:{meme.url}")

    async def validate_upload(self, sender_id: int, meme: models.Meme):
        pass
    