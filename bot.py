from vkwave.bots import DefaultRouter, BotEvent, FromIdFilter, AttachmentTypeFilter, RegexFilter
import dateparser
from download import download
import sqlighter
import post
import re
from datetime import datetime
import time
import io



class Bot():
    def __init__(self, router: DefaultRouter, database: sqlighter.SQLighter, **config):
        self.router = router
        self.database = database
        self.config = config
        router.register_handler(RegexFilter(r"add (\d+) (\d+) (\w+)"), FromIdFilter(config["id"]), callback=self.add_user)
        router.register_handler(RegexFilter(r"remove (\d+)"), FromIdFilter(config["id"]), callback=self.remove_user)
        router.register_handler(FromIdFilter(self.ids), AttachmentTypeFilter(attachment_type="photo"), callback=self.schedule_meme)
        router.register_handler(callback=self.other)
        

        self.ids = []

        
    def post_vk(group_id: int, date_time: datetime, attachment: io.BytesIO):
        return self.vk_api.wall.post(owner_id = group_id, from_group = True, attachments = attachment,publish_date = int(time.mktime(date_time.timetuple())))

    def get_user_ids(self)->list[int]:
        self.ids = self.database.get_users()
        
    @staticmethod
    def sort_photos(photos: list):
        return map(lambda x: sorted(x.photo.sizes, key = lambda x : x.width*x.height)[-1], photos)

    async def schedule_meme(self, event: BotEvent):
        if not event.text:
            return "NO text found"
        
        if event.text.startwith("vk"):
            chanel_types = "vk"
            text = event.text[2:]
        if event.text.startwith("telegram"):
            channel_type = "telegram"
            text = event.text[8:]
        
        texts = text.split(", ")
        times = map(dateparser.parse,texts)
        chanels = self.get_user(event.from_id)
        if chanel_types:
            chanels = filter(lambda x:x[2] == chanel_types, chanels)

        photos_urls = Bot.sort_photos(event.attachments)
        for time, photo in zip(times,photos_urls):
            photo_bytes = download(photo.url)
            for channel in chanels:
                channel_type = channel[2]
                group_id = channel[1]
            if channel_type == "vk":
                #!
                post.post_vk(group_id, time, photo_bytes)
            if channel_type == "telegram":
                #!
                post.post_telegram(group_id, time, photo_bytes)

        await event.answer("Succesful")

    async def add_user(self, event: BotEvent):
        match = re.match(r"add (\d+) (\d+) (\w+)")
        user_id = int(match.group(1))
        group_id = int(match.group(2))
        channel_type = match.group(3)
        await self.database.add_user(user_id, group_id, channel_type)
        return f"Succesfull added new user {user_id}"

    async def remove_user(self, event: BotEvent):
        match = re.match(r"remove (\d+)")
        user_id = int(match.group(1))
        await self.database.remove_user(user_id)
        return f"User {user_id} removed"


    def other(self, event: BotEvent):
        return f"You are unavalible to post or wrong data \n please contact {self.config['link']}"
