from vkwave.bots import SimpleLongPollBot, DefaultRouter
from vkwave.api import API
import aiogram
import json
from bot import Bot
import sqlighter
import asyncio


with open("config.json", 'r', encoding = "utf-8") as config:
    config = json.load(config)
    downloader = config["downloader"]
    VUploader = config["vk_uploader"]
    TUploader = config["telegram_uploader"]

downloader = SimpleLongPollBot(**downloader)
vk_uploader = API(**VUploader)
vk_uploader = vk_uploader.get_context()
telegram_uploader = aiogram.Bot(**TUploader)
telegram_dispatcher = aiogram.Dispatcher(telegram_uploader)


"""adding router"""
message_router = DefaultRouter()
vk_uploader.add(message_router)
database = asyncio.run(sqlighter.SQLighter("data.db")) 
vk_bot = Bot(router,database,link="[vk.com/travetin35|travetin35]",id = 507016336)

downloader.run_forever()
